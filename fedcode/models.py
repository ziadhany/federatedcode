#
# Copyright (c) nexB Inc. and others. All rights reserved.
# FederatedCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/federatedcode for support or download.
# See https://aboutcode.org for more information about AboutCode.org OSS projects.
#

import uuid
from urllib.parse import urljoin

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from git import Repo

from fedcode.utils import ap_collection
from fedcode.utils import clone_git_repo
from fedcode.utils import full_reverse
from fedcode.utils import generate_webfinger
from federatedcode.settings import FEDERATEDCODE_DOMAIN
from federatedcode.settings import FEDERATEDCODE_WORKSPACE_LOCATION


class RemoteActor(models.Model):
    """
    Represent a remote actor with its username
    """

    url = models.URLField(
        primary_key=True,
    )

    username = models.CharField(
        max_length=100,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="A field to track when remote actor are created",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="A field to track when remote actor are updated",
    )

    @property
    def safe_url(self):
        return f"{self.url.rstrip('/')}/"


class Actor(models.Model):
    """
    Represent a local or remote actor
    """

    summary = models.CharField(
        help_text="profile summary",
        max_length=100,
    )

    public_key = models.TextField(
        blank=False,
    )

    class Meta:
        abstract = True


class Reputation(models.Model):
    """
    Reputation of a package or vulnerability.

    https://www.w3.org/TR/activitystreams-vocabulary/#dfn-like
    https://www.w3.org/ns/activitystreams#Dislike
    """

    voter = models.CharField(
        max_length=100,
        help_text="security@vcio",
    )

    positive = models.BooleanField(
        default=True,
    )  # Like vs Dislike

    limit = models.Q(app_label="fedcode", model="review") | models.Q(
        app_label="fedcode", model="note"
    )

    content_type = models.ForeignKey(
        ContentType,
        limit_choices_to=limit,
        on_delete=models.CASCADE,
    )

    object_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
    )

    content_object = GenericForeignKey(
        "content_type",
        "object_id",
    )

    class Meta:
        unique_together = [["voter", "content_type", "object_id"]]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    @property
    def to_ap(self):
        return {
            "type": "Like" if self.positive else "Dislike",
            "actor": self.voter,
            "object": self.content_object.to_ap,
        }


class Service(models.Model):
    """
    A Service is a special user that can manage git repositories ( sync , create )
    """

    user = models.OneToOneField(
        User,
        null=True,
        on_delete=models.CASCADE,
    )

    remote_actor = models.OneToOneField(
        RemoteActor,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.user.username if self.user else self.remote_actor.username

    @property
    def absolute_url_ap(self):
        return full_reverse("user-ap-profile", self.user.username)

    @property
    def to_ap(self):
        return {
            "type": "Service",  # TODO
            "name": self.user.username,
        }


class Note(models.Model):
    """
    A Note is a message send by a Person or Package.
    The content is either a plain text message or structured YAML.
    If the author is a Package actor then the content is always YAML
    If the author is a Person actor then the content is always plain text
    https://www.w3.org/TR/activitystreams-vocabulary/#dfn-note
    """

    # https://www.w3.org/TR/activitystreams-vocabulary/#dfn-mediatype
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text="The object's unique global identifier",
    )

    acct = models.CharField(
        max_length=200,
        help_text="Account that created this note",
    )

    content = models.TextField(
        help_text="Text content for this note",
    )

    reply_to = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replies",
        help_text="",
    )

    mediaType = models.CharField(
        max_length=20,
        default="text/plain",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="A field to track when notes are created",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="A field to track when notes are updated",
    )

    reputation = GenericRelation(
        Reputation,
    )

    class Meta:
        ordering = ["-updated_at"]

    @property
    def username(self):
        return self.acct.split("@")[0]

    @property
    def reputation_value(self):
        return (
            self.reputation.filter(positive=True).count()
            - self.reputation.filter(positive=False).count()
        )

    @property
    def absolute_url(self):
        return full_reverse("note-page", self.id)

    @property
    def acct_avatar(self):
        person = Person.objects.get(user__username=self.username)
        return person.avatar

    @property
    def to_ap(self):
        return {
            "id": self.absolute_url,
            "type": "Note",
            "author": self.acct,
            "content": self.content,
            "update_date": str(self.updated_at),
        }


class Package(Actor):
    """
    A software package is an Actor identified by its package url ( PURL ) ignoring versions
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="The object's unique global identifier",
    )

    remote_actor = models.OneToOneField(
        RemoteActor,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    service = models.ForeignKey(
        Service,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    purl = models.CharField(
        max_length=300,
        help_text="PURL (no version) ex: @pkg:maven/org.apache.logging",
        unique=True,
    )

    notes = models.ManyToManyField(
        Note,
        blank=True,
        help_text="""the notes created by this package""",
    )

    class Meta:
        ordering = ["purl"]

    @property
    def acct(self):
        return generate_webfinger(self.purl)

    def __str__(self):
        return self.purl

    @property
    def followers_count(self):
        return Follow.objects.filter(package=self).count()

    @property
    def notes_count(self):
        return Note.objects.filter(acct=self.acct).count()

    @property
    def followers(self):
        return Follow.objects.filter(package=self).values("person_id")

    @property
    def followers_inboxes(self):
        """Return a followers inbox list"""
        # TODO Try to avoid for loop
        inboxes = []
        for person in self.followers:
            person_inbox = Person.objects.get(id=person["person_id"]).inbox_url
            inboxes.append(person_inbox)
        return inboxes

    # TODO raise error if the package have a version or qualifiers or subpath
    # def save(self, *args, **kwargs):
    #     if not check_purl_actor(self.string):
    #         return ValidationError(self.string)
    #     super(Purl, self).save(*args, **kwargs)

    @property
    def absolute_url_ap(self):
        return full_reverse("purl-ap-profile", self.purl)

    @property
    def inbox_url(self):
        return full_reverse("purl-inbox", self.purl)

    @property
    def outbox_url(self):
        return full_reverse("purl-outbox", self.purl)

    @property
    def followers_url(self):
        return full_reverse("purl-followers", self.purl)

    @property
    def key_id(self):
        return full_reverse("purl-ap-profile", self.purl)

    @property
    def to_ap(self):
        return {
            "id": self.absolute_url_ap,
            "type": "Package",
            "name": self.service.user.username,
            "purl": self.purl,
            "inbox": self.inbox_url,
            "outbox": self.outbox_url,
            "followers": self.followers_url,
            "publicKey": {
                "id": self.absolute_url_ap,
                "owner": self.service.absolute_url_ap,
                "publicKeyPem": "-----BEGIN PUBLIC KEY-----...-----END PUBLIC KEY-----",
            },
        }


class Person(Actor):
    """
    A person is a user can follow package or just vote or create a notes
    """

    user = models.OneToOneField(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    remote_actor = models.OneToOneField(
        RemoteActor,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    notes = models.ManyToManyField(
        Note,
        blank=True,
        help_text="Notes created by this user",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(user__isnull=False, remote_actor__isnull=True)
                    | models.Q(user__isnull=True, remote_actor__isnull=False)
                ),
                name="either_local_or_remote",
            ),
        ]

    @property
    def avatar(self):
        from hashlib import sha256

        email = ""
        if self.user and (email := self.user.email):
            email = email.strip().lower()

        gravatar = sha256(email.encode("utf-8")).hexdigest()
        return f"https://gravatar.com/avatar/{gravatar}"

    @property
    def local(self):
        return bool(self.user)

    @property
    def avatar_absolute_url(self):
        return self.avatar

    # TODO raise error if the user doesn't have a user or remote actor
    @property
    def reputation_value(self):
        """if someone like your ( review or note ) you will get +1, dislike: -1"""
        # user_reputation = Reputation.objects.filter(voter=self.acct)
        # return (
        #         user_reputation.filter(positive=True).count()
        #         - user_reputation.filter(positive=False).count()
        # )
        return 0  # FIXME

    @property
    def acct(self):
        return generate_webfinger(self.user.username)

    @property
    def url(self):
        return full_reverse("user-profile", self.user.username)

    @property
    def absolute_url_ap(self):
        return full_reverse("user-ap-profile", self.user.username)

    @property
    def inbox_url(self):
        if not self.local:
            return urljoin(self.remote_actor.safe_url, "inbox")
        return full_reverse("user-inbox", self.user.username)

    @property
    def outbox_url(self):
        if not self.local:
            return urljoin(self.remote_actor.safe_url, "outbox")
        return full_reverse("user-outbox", self.user.username)

    @property
    def following_url(self):
        return full_reverse("user-following", self.user.username)

    @property
    def key_id(self):
        if self.user:
            return full_reverse("user-ap-profile", self.user.username) + "#main-key"
        else:
            return self.remote_actor.safe_url + "#main-key"

    @property
    def to_ap(self):
        name = self.user.username if self.local else self.remote_actor.username
        return {
            "id": self.absolute_url_ap,
            "type": "Person",
            "name": name,
            "summary": self.summary,
            "inbox": self.inbox_url,
            "outbox": self.outbox_url,
            "following": self.following_url,
            "image": self.avatar_absolute_url,
            "publicKey": {
                "id": self.absolute_url_ap,
                "owner": self.absolute_url_ap,
                "publicKeyPem": "-----BEGIN PUBLIC KEY-----...-----END PUBLIC KEY-----",
            },
        }


class Follow(models.Model):
    """
    A Follow relates a person to a package that "follows" a package.
    """

    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        help_text="Person that follows",
    )

    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        help_text="Followed package",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date created",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date updated",
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        username = self.person.remote_actor.username
        if self.person.local:
            username = self.person.user.username
        return f"{username} - {self.package.purl}"


class Repository(models.Model):
    """
    A git repository used as a backing storage for Package and vulnerability data
    """

    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text="The object's unique global identifier",
    )

    url = models.URLField(
        help_text="Git Repository url ex: https://github.com/nexB/vulnerablecode-data",
    )

    path = models.CharField(
        max_length=200,
        help_text="path of the repository",
    )

    admin = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        help_text="admin user ex: VCIO user",
    )

    remote_url = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        help_text="the url of the repository" " if this repository is remote",
    )

    last_imported_commit = models.CharField(
        max_length=64,
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="A field to track when repository are created",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="A field to track when repository are updated",
    )

    class Meta:
        unique_together = [["admin", "url"]]
        ordering = ["-updated_at"]

    def __str__(self):
        return self.url

    @property
    def review_count(self):
        return Review.objects.filter(repository=self).count()

    @property
    def git_repo_obj(self):
        return Repo(self.path)

    @property
    def absolute_url(self):
        return full_reverse("repository-page", self.id)

    @property
    def to_ap(self):
        return {
            "id": self.absolute_url,
            "type": "Repository",
            "url": self.url,
        }


class Vulnerability(models.Model):
    """
    A vulnerability tracked by its VulnerableCode VCID
    """

    id = models.CharField(
        primary_key=True,
        max_length=20,
        help_text="Unique vulnerability identifier 'VCID'",
    )

    repo = models.ForeignKey(
        Repository,
        on_delete=models.CASCADE,
    )

    remote_url = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        help_text="",
    )

    class Meta:
        unique_together = ("id", "repo")

    @property
    def absolute_url(self):
        return full_reverse("vulnerability-page", self.id)

    def __str__(self):
        return self.id

    @property
    def to_ap(self):
        return {
            "id": self.absolute_url,
            "type": "Vulnerability",
            "repository": self.repo.absolute_url,
        }


class Review(models.Model):
    """
    A review tracks the review comments on a Package or Vulnerability.
    """

    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text="The object's unique global identifier",
    )

    headline = models.CharField(
        max_length=300,
        help_text="the review title",
    )

    author = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
    )

    repository = models.ForeignKey(
        Repository,
        on_delete=models.CASCADE,
    )

    filepath = models.CharField(
        max_length=300,
        help_text="the review path ex: /apache/httpd/VCID-1a68-fd5t-aaam.yml",
    )

    commit = models.CharField(
        max_length=300,
        help_text="ex: 104ccd6a7a41329b2953c96e52792a3d6a9ad8e5",
    )

    data = models.TextField(
        help_text="review data ex: vulnerability file",
    )

    notes = models.ManyToManyField(
        Note,
        blank=True,
        help_text="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="A field to track when review are created",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="A field to track when review are updated",
    )

    remote_url = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        help_text="the review remote url if " "Remote Review exists",
    )

    class ReviewStatus(models.IntegerChoices):
        OPEN = 0
        DRAFT = 1
        CLOSED = 2
        MERGED = 3

    status = models.SmallIntegerField(
        choices=ReviewStatus.choices,
        null=False,
        blank=False,
        default=0,
        help_text="status of review",
    )

    reputation = GenericRelation(
        Reputation,
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.headline}"

    @property
    def reputation_value(self):
        return (
            self.reputation.filter(positive=True).count()
            - self.reputation.filter(positive=False).count()
        )

    @property
    def absolute_url(self):
        return full_reverse("review-page", self.id)

    @property
    def to_ap(self):
        return {
            "id": self.absolute_url,
            "type": "Review",
            "author": self.author.absolute_url_ap,
            "headline": self.headline,
            "repository": str(self.repository.id),
            "filepath": self.filepath,
            "commit": self.commit,
            "content": self.data,
            "comments": ap_collection(self.notes),
            "published": self.created_at,
            "updated": self.updated_at,
        }


class FederateRequest(models.Model):
    target = models.URLField(
        help_text="The request target ex: (inbox of the targeted actor",
        blank=False,
        null=False,
    )

    body = models.TextField(
        help_text="The request body",
        blank=False,
        null=False,
    )

    key_id = models.URLField(
        help_text="The key url of the actor ex: https://my-example.com/actor#main-key",
        blank=False,
        null=False,
    )

    error_message = models.TextField(
        help_text="Error message if a request failed to federate",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="A field to track when review are created",
    )

    done = models.BooleanField(
        default=False, help_text="Flag set to true when the request completed"
    )


class SyncRequest(models.Model):
    repo = models.ForeignKey(
        Repository,
        on_delete=models.CASCADE,
        help_text="The Git repository where the importer will run",
    )

    error_message = models.TextField(
        help_text="Error message if a request failed to sync",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="A field to track when review are created",
    )

    done = models.BooleanField(
        default=False, help_text="Flag set to true when the request completed"
    )


@receiver(post_save, sender=Repository)
def create_git_repo(sender, instance, created, **kwargs):
    if created:
        repo = clone_git_repo(FEDERATEDCODE_WORKSPACE_LOCATION, instance.url)
        instance.path = repo.working_dir
        instance.save()
