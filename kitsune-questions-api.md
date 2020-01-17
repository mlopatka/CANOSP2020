'Kitsune' is the code name for the django based software that powers support.mozilla.org

# Kitsune Questions API

Base URL: `https://support.mozilla.org/`

# Endpoint:

```
api/2/question/?format=json&ordering=-updated&is_spam=False&created__gt=<time_in_PST>&created__lt=<time_in_PST>
```

e.g.:

```
api/2/question/?format=json&ordering=-updated&is_spam=False&created__gt=2019-05-13%2007:53:39&created__lt=2019-05-13%2007:53:41
```
