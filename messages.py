class Messages:
    def __init__(self):

        # Success output messages
        self.success_post_tweet = "Success! Your tweet '{}' was posted on {}."
        self.success_get_list_members = "Success! All {} member {}s have been collected from @{}'s list '{}'."
        self.success_get_list_member_data = "Success! Data for {}'s list '{}' has been retrieved."
        self.success_get_owner_lists = "Success! All {} lists have been retrieved from {}."
        self.success_get_owner_list_data = "Success! Data for all {} of {}'s lists has been retrieved."
        self.success_get_my_lists = "Success! All {} of your lists have been retrieved."
        self.success_get_my_list_data = "Success! Data for all {} of your lists has been retrieved."
        self.success_create_list = "List '{}' created on {} with {} members."
        self.success_copy_list = "List '{}' with slug '{}' copied from @{} on {}."
        self.success_delete_all_lists = "All {} of your lists have been deleted."
        self.success_delete_all_tweets = 'Success! All {} of your statuses have been deleted.'

        # Error output messages
        self.error_get_my_lists = "You have no lists to retrieve..."
        self.error_get_my_list_data = "You have no list data to retrieve..."
        self.error_get_ids_from_names = "User {} not found. Double check screen_name or id to make sure it is valid."
        self.error_create_list = "Could not add member '{}'. Resuming after 60 seconds..."
        self.error_create_list_path = "The argument 'members = ' must contain either a list object or an absolute path to a file containing the list of members."
        self.error_delete_all_lists = "You don't have any lists to delete."
        self.error_delete_all_tweets = 'You have no tweets to delete.'
