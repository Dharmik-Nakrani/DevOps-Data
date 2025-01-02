# Setup SSH and GPG

## _SSH_

- Generate SSH key via terminal or CMD
```sh
ssh-keygen -t rsa -b 4096 -c "companymail@mail.com"
```
- Enter Path and key name for better identification
>  - /home/username/.ssh/company
>  - Enter passphrase (optionlly)
>  - again enter passphrase (optionlly)
-  Open SSH key and copy it
```
cat ~/.ssh/company.pub
```
-  Put this SSH Key in Github
>  - Account -> Setting -> SSH and GPG Key -> New SSH Key
-  Add this SSH key in System
```
ssh-add ~/.ssh/company
```

> Note: `Test Clone using SSH URL`.


## _GPG_
> Note: `For GPG Setup you need to required SSH`.

- Install gnupg
- Generate GPG key
> ```sh
> gpg --full-generate-key
> ```
> - 0.Select 1 (RSA and RSA)
> - 1.Enter keysize: 4096
> - 2.Select 0 (key does not expire)
> - 3.Press : y (Yes)
> - 4.Enter identify of company (Realname: Giithub Username, Email Address: Github Email Address)
> - 5.Press :O (Okay)
> - 6.Enter Passcode which is use every time when you commit

-   Verify Your GPG Key
```
gpg --list-secret-keys --keyid-format long
```
-  export GPG key
```
gpg --armor --export
```
- Copy and put this full key in Github
>   Account -> Setting -> SSH and GPG Key -> New GPG Key
- Add GPG Signing in Your Repo
```sh
gpg --list-secret-keys --keyid-format long
```
> [!NOTE]
```
sec   rsa4096/`EB6D4BF827C5CCBD` 2024-07-11 [SC]
     A8ED30FD1FD9DDBA743C066AEB6D4BF827C5CCBD
uid                 [ultimate] Dharmik Nakrani (Dharmik GPG Key) > <dharmik.n@healtech.au>
ssb   rsa4096/E0761A0FDF469301 2024-07-11 [E]
```
- Enter in your repo
```
git config --global commit.gpgSign true
git config --global user.signingKey `highlighted key`
```

> Note: `Test When you commit any thing it required Passcode`.
