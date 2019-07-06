# Linux User Setup Notes

## /etc/passwd

Stores users. Each line represents one user, in the following format:

~~~
[User name]:[Password]:[UID]:[GID]:[Full name]:[Home dir]:[Login shell]

root:x:0:0:root:/root:/bin/bash
lunariel:x:1000:1000:lunariel:/home/lunariel:/bin/bash
nfsnobody:x:65534:65534:Anonymous NFS User:/var/lib/nfs:/sbin/nologin
~~~

- `[Password]`: 'x' or '*' here indicates password is stored in `/etc/shadow`
- `[UID]`: Linux User ID. Unique unsigned integer, may be 16 or 32 bits depending on platform. 0 is reserved for root and 65534 for 'nobody'
- `[GID]`: Linux Group ID. Follows the same rules as the UID, and is usually equal to the UID
- `[Full name]`: Not really important. Usually either the same as the user name or a more description version of it
- `[Home dir]`: Home directory
- `[Login shell]`: Normally /bin/bash, set to /bin/false to disable login

## /etc/group

Stores groups. Each line represents one user, in the following format:

~~~
[Group name]:[Password]:[GID]:[Member 1]:[Member 2]:...

root:x:0:0:root:/root:/bin/bash
lunariel:x:1000:1000:lunariel:/home/lunariel:/bin/bash
nfsnobody:x:65534:65534:Anonymous NFS User:/var/lib/nfs:/sbin/nologin
~~~

- `[Password]`: 'x' or '*' here indicates password is stored in `/etc/shadow`
- `[GID]`: Linux Group ID. Follows the same rules as the UID, and is usually equal to the UID
- `[Member *]`: Members are designated by user name. The member list is not required and should be left blank for personal groups

There should be a personal group for each user, with the same name as the user.

## /etc/shadow

Stores passwords. If using a shadow file, each line in `/etc/passwd` should have a corresponding line in the shadow file, in the same order. The shadow file should only be readable to root. Each line is formatted as follows:

`[User name]:$[Algorithm]$[Salt]$[Hash]:[Days since change epoch]:[Days until change allowed]:[Days until expiration]:[Days warning before expiration]:[Days before account inactive]:[Days since expiration epoch]:[Reserved]`

Most of these fields can be ignored, leaving:

~~~
[User name]:$[Algorithm]$[Salt]$[Hash]::0:99999:7:::

root:$6$gzyP4x62WlobnTqm$[Hash]::0:99999:7:::
lunariel:$6$LoCFUrT9ebg6r6Sv$[Hash]::0:99999:7:::
nfsnobody:!!:16737::::::
~~~

The entire second field can be replaced with an empty string for no password, or '!', '!!', '*', or 'LK' to indicated a locked account
