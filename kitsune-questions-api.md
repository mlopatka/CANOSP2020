'Kitsune' is the code name for the django based software that powers support.mozilla.org

# Kitsune Questions API

* Base URL: `https://support.mozilla.org/`
* Method: `GET`
* Content Type: ``application/json``
* Response: ``application/json``

# Endpoint:

```
api/2/question/?format=json&ordering=-updated&is_spam=False&created__gt=<time_in_PST>&created__lt=<time_in_PST>
```

e.g.:

```
api/2/question/?format=json&ordering=-updated&is_spam=False&created__gt=2019-05-13%2007:53:39&created__lt=2019-05-13%2007:53:41
```

# Responses

All response bodies are in JSON.

# HTTP 200: Success

With an HTTP 200, you'll get back a set of results in JSON.

# Known Bugs

1. All times returned by the API are in PST not PDT and not UTC
2. All URL parameters for time are also in PST not UTC

See https://github.com/mozilla/kitsune/issues/3961 and https://github.com/mozilla/kitsune/issues/3946
    
# Example Request

```bash
curl -X GET "https://support.mozilla.org/api/2/question/?format=json&ordering=-updated
&is_spam=False\
&created__gt=2019-05-13%2007:53:39&created__lt=2019-05-13%2007:53:41"
```

# Example Response

```
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "answers": [
        1222018,
        1222044,
        1222056,
        1222067,
        1222070,
        1222071,
        1222125,
        1222128,
        1222302,
        1222414,
        1222423,
        1225628
      ],
      "content": "<p>Morning,\n</p><p>I've recently switched back to Firefox (for Mac) after being away from Ff for a long time, and have been tinkering with my settings and whatnot to try and get things the way I would like them. I suspect, like most things, that I'm just missing something. ;-)\n</p><p>Basically, I don't want Ff to remember any autofill//form information, and I've got that working, but I would like it to be able to respect when a website allows you to click a radio button for \"Remember &lt;Me//This//Etc&gt;\". It does not seem to be doing that at the moment.\n</p><p>Does Ff have a setting that will let websites that you specifically click \"Remember Me\" be remembered, or is it an all or nothing?\n</p><p>Thanks!\n</p>",
      "created": "2019-05-13T07:53:40Z",
      "creator": {
        "username": "mattagc",
        "display_name": null,
        "avatar": "https://secure.gravatar.com/avatar/f0e4c5328a02ad72767fc75385052804?s=48&d=https%3A//static-media-prod-cdn.itsre-sumo.mozilla.net/static/sumo/img/avatar.png"
      },
      "id": 1259114,
      "involved": [
        {
          "username": "jscher2000",
          "display_name": "jscher2000",
          "avatar": "https://firefoxusercontent.com/4c7c89d3462af52bac94074246fd5e98"
        },
        {
          "username": "mattagc",
          "display_name": null,
          "avatar": "https://secure.gravatar.com/avatar/f0e4c5328a02ad72767fc75385052804?s=48&d=https%3A//static-media-prod-cdn.itsre-sumo.mozilla.net/static/sumo/img/avatar.png"
        },
        {
          "username": "cor-el",
          "display_name": "",
          "avatar": "https://firefoxusercontent.com/f369028d14003acbf4f1a9ed0debb2c8"
        }
      ],
      "is_archived": true,
      "is_locked": false,
      "is_solved": false,
      "is_spam": false,
      "is_taken": false,
      "last_answer": 1225628,
      "locale": "en-US",
      "metadata": [
        {
          "name": "category",
          "value": "privacy-and-security"
        },
        {
          "name": "ff_version",
          "value": "66.0"
        },
        {
          "name": "os",
          "value": "Mac OS"
        },
        {
          "name": "plugins",
          "value": "* Shockwave Flash 32.0 r0"
        },
        {
          "name": "product",
          "value": "desktop"
        },
        {
          "name": "useragent",
          "value": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0"
        }
      ],
      "tags": [
        {
          "name": "Firefox 66.0",
          "slug": "firefox-660"
        },
        {
          "name": "privacy-and-security",
          "slug": "privacy-and-security_1"
        },  
        {
          "name": "desktop",
          "slug": "desktop"
        },
        {
          "name": "Mac OS",
          "slug": "mac-os"
        }
      ],
      "num_answers": 12,
      "num_votes_past_week": 0,
      "num_votes": 1,
      "product": "firefox",
      "solution": null,
      "solved_by": null,
      "taken_until": null,
      "taken_by": null,
      "title": "Firefox doesn't seem to be allowing websites to \"remember <random thing>\".",
      "topic": "privacy-and-security",
      "updated_by": null,
      "updated": "2019-05-27T19:18:25Z"
    }
  ]
}

```

# API for a single question

* Endpoint:
```
https://support.mozilla.org/api/2/question/<id>/
e.g.
https://support.mozilla.org/api/2/question/1271141/
```
* Sample code: https://github.com/rtanglao/rt-kits-api2/blob/master/test-time-question-1271141.rb

* Sample output in json

```json
{
                "answers" => [
        [0] 1260198,
        [1] 1260199,
        [2] 1260205
    ],
                "content" => "<p>My previous question: <a href=\"https://support.mozilla.org/en-US/questions/1254024\" rel=\"nofollow\">https://support.mozilla.org/en-US/questions/1254024</a>\n</p><p>With the latest update, the following css tweak to disable the creation of new tab when middle clicking the empty tab bar area no longer works.\n</p><p><a href=\"https://pastebin.com/zSJYR8PJ\" rel=\"nofollow\">https://pastebin.com/zSJYR8PJ</a>\n</p><p>This along with the shortcut CTRL+SHIFT+P to open a new private window are features no other browsers have.\n</p>",
                "created" => "2019-10-23T00:02:46Z",
                "creator" => {
            "username" => "ZetiX",
        "display_name" => "ZetiX",
              "avatar" => "https://firefoxusercontent.com/00000000000000000000000000000000"
    },
                     "id" => 1271141,
               "involved" => [
        [0] {
                "username" => "jscher2000",
            "display_name" => "jscher2000",
                  "avatar" => "https://firefoxusercontent.com/4c7c89d3462af52bac94074246fd5e98"
        },
        [1] {
                "username" => "ZetiX",
            "display_name" => "ZetiX",
                  "avatar" => "https://firefoxusercontent.com/00000000000000000000000000000000"
        },
        [2] {
                "username" => "cor-el",
            "display_name" => "",
                  "avatar" => "https://firefoxusercontent.com/f369028d14003acbf4f1a9ed0debb2c8"
        }
    ],
            "is_archived" => false,
              "is_locked" => false,
              "is_solved" => true,
                "is_spam" => false,
               "is_taken" => false,
            "last_answer" => 1260205,
                 "locale" => "en-US",
               "metadata" => [
        [0] {
             "name" => "category",
            "value" => "tabs"
        },
        [1] {
             "name" => "ff_version",
            "value" => "70.0"
        },
        [2] {
             "name" => "os",
            "value" => "Windows 10"
        },
        [3] {
             "name" => "product",
            "value" => "desktop"
        },
        [4] {
             "name" => "solver_id",
            "value" => "1473644"
        },
        [5] {
             "name" => "useragent",
            "value" => "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0"
        }
    ],
                   "tags" => [
        [0] {
            "name" => "tabs",
            "slug" => "tabs"
        },
        [1] {
            "name" => "Firefox 70.0",
            "slug" => "firefox-700"
        },
        [2] {
            "name" => "desktop",
            "slug" => "desktop"
        },
        [3] {
            "name" => "Windows 10",
            "slug" => "windows-10"
        },
        [4] {
            "name" => "unsupported",
            "slug" => "unsupported"
        },
        [5] {
            "name" => "unsupporteduserchrome.css",
            "slug" => "unsupporteduserchromecss"
        },
        [6] {
            "name" => "unsuppportedhacks",
            "slug" => "unsuppportedhacks"
        },
        [7] {
            "name" => "userchrome.css",
            "slug" => "userchromecss"
        }
    ],
            "num_answers" => 3,
    "num_votes_past_week" => 1,
              "num_votes" => 1,
                "product" => "firefox",
               "solution" => 1260198,
              "solved_by" => {
            "username" => "jscher2000",
        "display_name" => "jscher2000",
              "avatar" => "https://firefoxusercontent.com/4c7c89d3462af52bac94074246fd5e98"
    },
            "taken_until" => nil,
               "taken_by" => nil,
                  "title" => "Disable middle click tab bar",
                  "topic" => "tabs",
             "updated_by" => {
            "username" => "ZetiX",
        "display_name" => "ZetiX",
              "avatar" => "https://firefoxusercontent.com/00000000000000000000000000000000"
    },
                "updated" => "2019-10-23T02:11:10Z"
}
```



