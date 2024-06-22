from django import forms
from .models import Transaction
from accounts.models import UserBankAccount

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'amount',
            'transaction_type'
        ]

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account') # account value ke pop kore anlam
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True # ei field disable thakbe
        self.fields['transaction_type'].widget = forms.HiddenInput() # user er theke hide kora thakbe

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()


class DepositForm(TransactionForm):
    def clean_amount(self): # amount field ke filter korbo
        min_deposit_amount = 100
        amount = self.cleaned_data.get('amount') # user er fill up kora form theke amra amount field er value ke niye aslam, 50
        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposit_amount} $'
            )

        return amount


class WithdrawForm(TransactionForm):

    def clean_amount(self):
        account = self.account
        min_withdraw_amount = 500
        max_withdraw_amount = 20000
        balance = account.balance # 1000
        amount = self.cleaned_data.get('amount')
        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at least {min_withdraw_amount} $'
            )

        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at most {max_withdraw_amount} $'
            )

        if amount > balance: # amount = 5000, tar balance ache 200
            raise forms.ValidationError(
                f'You have {balance} $ in your account. '
                'You can not withdraw more than your account balance'
            )

        return amount



class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        return amount
    

class TransferForm(TransactionForm):
    target_account_id = forms.IntegerField(label="Target Account ID")

    class Meta(TransactionForm.Meta):
        fields = TransactionForm.Meta.fields + ['target_account_id']

    def clean(self):
        cleaned_data = super().clean()
        target_account_id = cleaned_data.get('target_account_id')
        amount = cleaned_data.get('amount')
        
        if target_account_id:
            try:
                target_account = UserBankAccount.objects.get(account_no=target_account_id)
                if target_account == self.account:
                    raise forms.ValidationError("You cannot transfer money to the same account.")
                cleaned_data['target_account'] = target_account
            except UserBankAccount.DoesNotExist:
                raise forms.ValidationError(f"No account found with ID {target_account_id}")
        
        if amount:
            if amount > self.account.balance:
                raise forms.ValidationError("You do not have enough balance to complete this transfer.")
        
        return cleaned_data

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance - self.cleaned_data['amount']
        self.instance.transaction_type = 5  
        
        target_account = self.cleaned_data['target_account']
        target_account.balance += self.cleaned_data['amount']
        if commit:
            target_account.save()
            self.account.balance -= self.cleaned_data['amount']
            self.account.save()
            self.instance.save()
        
        
        Transaction.objects.create(
            account=target_account,
            amount=self.cleaned_data['amount'],
            balance_after_transaction=target_account.balance,
            transaction_type=6,  
        )
        
        return self.instance