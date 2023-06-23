# step 1

На windows 11 у меня не работает ssh forwarding. Вероятно, из-за разных версий. Поэтому если предполагается работа с git, то нужно из Ubuntu подключатся. В selectel добавлены SSH-ключи пользователя root и для Windows и для Ubuntu.

```
ssh-add (в Ubuntu)
ssh myselectel
```


# step 3

windows 11: C:\Users\dima\.ssh 
```
Host myselectel
    HostName 77.105.168.57
    User root
    ForwardAgent yes
```