#
# Copyright (c) nexB Inc. and others. All rights reserved.
# FederatedCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/federatedcode for support or download.
# See https://aboutcode.org for more information about AboutCode.org OSS projects.
#

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Note
from .models import Repository
from .models import Review


class CreateGitRepoForm(forms.ModelForm):
    class Meta:
        model = Repository
        fields = ["url"]

    def __init__(self, *args, **kwargs):
        super(CreateGitRepoForm, self).__init__(*args, **kwargs)
        self.fields["url"].widget.attrs.update(
            {"class": "input", "placeholder": "https://github.com/nexB/vulnerablecode-data"}
        )
        self.fields["url"].help_text = ""
        self.fields["url"].label = ""


class CreateNoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["content"]

    def __init__(self, *args, **kwargs):
        super(CreateNoteForm, self).__init__(*args, **kwargs)
        self.fields["content"].widget.attrs.update(
            {"class": "textarea", "placeholder": "Comment...", "rows": 5}
        )
        self.fields["content"].label = ""
        self.fields["content"].help_text = ""


class ReviewStatusForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["status"]
        help_texts = {
            "status": None,
        }

    def __init__(self, *args, **kwargs):
        super(ReviewStatusForm, self).__init__(*args, **kwargs)
        self.fields["status"].widget.attrs.update({"class": "input mb-5"})


class PersonSignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )


class CreateReviewForm(forms.Form):
    headline = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "input is-medium title has-text-centered",
                "placeholder": "Review Title",
            }
        )
    )
    data = forms.CharField(widget=forms.Textarea(attrs={"class": "textarea", "rows": 16}))
    filename = forms.CharField(widget=forms.HiddenInput())


class FetchForm(forms.Form):
    file_path = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "placeholder": "alpine/dia/VCID-xxx-xxx-xxx.yaml",
            }
        )
    )


class SubscribePackageForm(forms.Form):
    acct = forms.CharField(
        label="Subscribe with a remote account:",
        widget=forms.TextInput(
            attrs={"placeholder": "ziadhany@vulnerablecode.io", "class": "input"}
        ),
    )


class SearchPackageForm(forms.Form):
    search = forms.CharField(
        required=True,
        label=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search a package...",
                "class": "input ",
            },
        ),
    )


class SearchReviewForm(forms.Form):
    search = forms.CharField(
        required=True,
        label=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Please Enter a valid Review Name",
                "class": "input is-rounded",
                "style": "width: 90%;",
            },
        ),
    )


class SearchRepositoryForm(forms.Form):
    search = forms.CharField(
        required=True,
        label=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search a repository...",
                "class": "input",
            },
        ),
    )
