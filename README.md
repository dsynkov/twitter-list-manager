
# Twitter List Manager

This module provides a set of functions build on top of [`tweepy`](https://github.com/tweepy/tweepy) for users to scrape, analyze, export, and copy publically available list on Twitter -- or alternatively, create and manage their own. It may be useful for those looking to get lists in or out of Twitter quickly in bulk for use in other kinds of analysis (digitial analytics or social listening) without necessarily requiring the larger extent of `tweepy`'s capabilities. More updates and features to come. 

## Getting Authenticated

***(There are many ways to set up authentication - this is just one approach that consistently works for me.)***

Create an app using your Twitter account and store the following variables in the `source.sh` template file, which you'll use to export your keys and tokens as environment variables. 

`$ export CONSUMER_KEY='YOUR CONSUMER_KEY HERE'`

`$ export CONSUMER_SECRET='YOUR CONSUMER_KEY HERE'`

`$ export ACCESS_TOKEN='YOUR ACCESS_TOKEN HERE'`

`$ export ACCESS_TOKEN_SECRET='YOUR ACCESS_TOKEN_SECRET HERE'`

`$ export OWNER='YOUR OWNDER NAME HERE'`

`$ export OWNER_ID='YOUR OWNER_ID HERE'`

In your terminal, run the following command:

`$ source source.sh`

To check that your environment variables have been stored, run the below command using any variable. I'll use `CONSUMER_KEY` in this example. If successful, you should see a print-out of your key.

`$ echo $CONSUMER_KEY`

To check these are being picked up by Python run the below commands in your Python console. You should see the same output as above.


```python
import os

print(os.environ.get('CONSUMER KEY'))
```

***(For Windows users, look up how to replicate the above steps using `setx` instead of `export` and a `.bat` instead of a `.sh` file. Or, just get the Bash emulator that comes with the installation of [Git for Windows](https://git-for-windows.github.io/).)***

Once your keys are squared away, you should be able to authenticate immediately after creating an instance of the `TwitterListManager()` class:


```python
from twitter_list_manager import TwitterListManager

t = TwitterListManager()
```

Now, post a tweet to verify authentication:


```python
t.post_tweet("Lets check out what we can do with Twitter lists!")
```

    Success! Your tweet 'Lets check out what we can do with Twitter lists!' was posted on 2017-11-17 22:12:01.
    

## Working With Public Lists

To get the list members from a publically available Twitter list, use the `.get_list_members()` method with the two required parameters of `owner` (the list owner's handle, sans '@', in quotes) and the list `slug`, also in quotes. We'll use the appropriately titled *Foreign Policy's* [Twitterati 100](https://twitter.com/foreignpolicy/lists/twitterati-100?lang=en). 

You should be able to find the slug in the tail-end portion of the URL, right before `lang` if `lang` is present. So, for a URL of `https://twitter.com/foreignpolicy/lists/twitterati-100?lang=en` the slug would be `twitterati-100`. This will return a `list` type object of user screen names.


```python
t.get_list_members('foreignpolicy','twitterati-100')
```

If you preffer user IDs instead of screen names, set `attr=` ("attribute") to `'id'`


```python
t.get_list_members('foreignpolicy','twitterati-100',attr='id')
```

To get list data -- or the entirety of the `tweepy` `List` object, use the `.get_list_member_data()` method. Set `export=` to `True` if you want it the data exported to `.csv`. The new file will be saved in the `exports` sub-directory of this repository. (`Export` is by default set to `False`.) This method will return a `pandas` dataframe.


```python
t.get_list_member_data('foreignpolicy','twitterati-100',export=True)
```

Now, to get a *list of lists* from a particular owner (user), simply pass the owner's handle (again, in quotes, and with no '@') to the `.get_owner_lists()` method, returning a `list` object.


```python
t.get_owner_lists('foreignpolicy')
```

Use `.get_owner_list_data()` for a more detailed look at a user's lists, including the full list name, description, count of subscribers, count of members, and the created time. Again, setting `export=` to `True` will write a `.csv` to your local directory. This method returns a dataframe.


```python
t.get_owner_list_data('foreignpolicy',export=True)
```

## Working With Your Own Lists

This next set of functions are parallel to the above, only you don't need to specify the `owner` parameter, since the owner is you (assuming you exported `OWNER` as an environment variable):


```python
t.get_my_lists() # Returns a list of your Twitter lists
```


```python
t.get_my_list_data(export=True) # Returns a dataframe of your list data
```

To create a list, you need to pass a name and either:

1. A Python list of screen names or Twitter ids you want added.
2. A file of screen names or Twitter ids you want added.

Note that if you're sourcing from your own file, `.csv,.txt,.xls`, and `.xlsx` are all supported, insofar as you are passing in an absolute path. The function will read in the first column of your file. Do not include headers.

**For *both* cases (1) & (2) above, the source has must be *all* screen names or *all* Twitter IDs.**

See the text files in the `examples` sub-directory of this repository for both cases.

Say we saved the *Foreign Policy* list from earlier into a list object and want to create a list from it outselves:


```python
twitterati = t.get_list_members('foreignpolicy','twitterati-100')
```

We can then pass it to the `.create_list()` method, preceded by a name.


```python
t.create_list('Twitterati Copy List',twitterati)
```

Alternatively, we can source our list from a file, using `list_as_text_file_ids.txt` as an example. Make sure you include an *absolute* (rather than a relative) filepath.


```python
filepath = '/c/path/to/twitter_list_manager/examples/list_as_text_file_ids.txt'

t.create_list('Twitterati Copy List',filepath)
```

You can also copy a publically available Twitter list to your own account:


```python
t.copy_list('foreignpolicy','twitterati-100')
```

    List 'Twitterati 100' with slug 'twitterati-100' copied from @foreignpolicy on 2017-11-04 01:28:40.
    

Lastly, to delete **all** of your lists, use the `.delete_all_lists()`. Please note this will delete **all** Twitter lists currently in your account. You you need to remove a single list, refer to the `API.destroy_list()` method in the [`tweepy` documentation](http://docs.tweepy.org/en/v3.5.0/api.html). 
