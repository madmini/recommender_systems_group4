from django import forms


class UserIdForm(forms.Form):
    user_id = forms.IntegerField(label='User ID:')

    def is_valid(self):
        valid = super(UserIdForm, self).is_valid()
        # max user count from https://www.kaggle.com/rounakbanik/the-movies-dataset/version/7#movies_metadata.csv
        # (ratings.small only has 671 users because used the data from assignment 2
        if (self.cleaned_data.get('user_id') > 0) and (self.cleaned_data.get('user_id') <= 671):
            # use a get_user_count method
            return True
        else:
            return False
