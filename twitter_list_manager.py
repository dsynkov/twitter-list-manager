# Import dependencies
import pandas as pd
import pathlib
import tweepy 
import json
import time
import os

# Import custom modules
from messages import Messages
import utils

auth_dict = {
    'CONSUMER_KEY': os.environ.get('CONSUMER_KEY'),
    'CONSUMER_SECRET': os.environ.get('CONSUMER_SECRET'),
    'ACCESS_TOKEN': os.environ.get('ACCESS_TOKEN'),
    'ACCESS_TOKEN_SECRET': os.environ.get('ACCESS_TOKEN_SECRET'),
    'OWNER': os.environ.get('OWNER'),
    'OWNER_ID': os.environ.get('OWNER_ID')
}


class TwitterListManager:

    def __init__(self):
        
        auth = tweepy.OAuthHandler(auth_dict['CONSUMER_KEY'], auth_dict['CONSUMER_SECRET'])
        auth.set_access_token(auth_dict['ACCESS_TOKEN'], auth_dict['ACCESS_TOKEN_SECRET'])
        
        self.OWNER = auth_dict['OWNER']
        self.OWNER_ID = auth_dict['OWNER_ID']
        
        self.API = tweepy.API(auth, wait_on_rate_limit=True)
        self.path = pathlib.PurePath(os.getcwd())
        self.msg = Messages()
    
    def post_tweet(self, text):

        self.API.update_status(status=text)
        
        ts = utils.get_timestamp()
            
        print(self.msg.success_post_tweet.format(text, ts))

    def get_list_members(self, owner, slug, attr='screen_name', export=True):
    
        output_list = []
        
        for member in tweepy.Cursor(self.API.list_members, owner, slug).items():
            if attr == 'id':
                output_list.append(member.id)
            else:
                output_list.append(member.screen_name)
                
        if export:
            utils.export_list(slug, output_list)
                
        print(self.msg.success_get_list_members.format(
            len(output_list), attr, owner, slug))  # To do: hide if used w/i function
        
        return output_list

    def get_list_member_data(self, owner, slug, export=False):
        member_df = pd.DataFrame()
        for member in tweepy.Cursor(self.API.list_members, owner, slug).items():
            # Create json string from User object
            member_json_str = json.dumps(member._json)
            # Read json into line as pandas df
            member_df_row = pd.read_json(member_json_str, lines=True)
            # Append each line into member_df
            member_df = member_df.append(member_df_row)
            # To do: write output to csv instead of a df
        if export:
            file_path = self.path / 'exports' / (slug + '-list-data.csv')
            member_df.to_csv(str(file_path))
            
        print(self.msg.success_get_list_member_data.format(
            owner, slug))
            
        return member_df

    def get_owner_lists(self, owner):
        list_result_set = self.API.lists_all(owner)
        list_names = []
        for item in list_result_set:
            list_names.append(item.name)
            
        print(self.msg.success_get_owner_lists.format(
           len(list_names), owner))
        
        return list_names

    def get_owner_list_data(self, owner, export=False):
        list_result_set = self.API.lists_all(owner)
        
        # Create fields
        list_names = []
        full_name = []
        description = []
        subscriber_count = []
        members_count = []
        created_at = []
        
        for item in list_result_set:
            list_names.append(item.name)
            full_name.append(item.full_name)
            description.append(item.description)
            subscriber_count.append(item.subscriber_count)
            members_count.append(item.member_count)
            created_at.append(item.created_at)
        list_df = pd.DataFrame({
            'list_name': list_names,
            'full_name': full_name,
            'description': description,
            'subscriber_count': subscriber_count,
            'members_count': members_count,
            'created_at': created_at
        })    
        
        if export:
            file_path = self.path / 'exports' / (owner + '-data.csv')
            list_df.to_csv(str(file_path))
            
        print(self.msg.success_get_owner_list_data.format(
            len(list_names), owner))
        
        return list_df

    def get_my_lists(self):
        
        list_result_set = self.API.lists_all(self.OWNER)
        
        list_names = []
        
        for item in list_result_set:
            list_names.append(item.name)
        
        if len(list_names) > 0:
            print(self.msg.success_get_my_lists.format(
                len(list_names)))
            
            return list_names
            
        print(self.msg.error_get_my_lists)

    def get_my_list_data(self, export=False):
              
        list_result_set = self.API.lists_all(self.OWNER)
        
        # Create fields
        list_names = []
        full_name = []
        description = []
        subscriber_count = []
        members_count = []
        created_at = []
        
        # To do: write to csv instead of a df
        # To do: option to return as List object
        for item in list_result_set:
            list_names.append(item.name)
            full_name.append(item.full_name)
            description.append(item.description)
            subscriber_count.append(item.subscriber_count)
            members_count.append(item.member_count)
            created_at.append(item.created_at)
        list_df = pd.DataFrame({
            'list_name': list_names,
            'full_name': full_name,
            'description': description,
            'subscriber_count': subscriber_count,
            'members_count': members_count,
            'created_at': created_at
        })    
        
        if export:
            file_path = self.path / 'exports' / (self.OWNER + '-list-data.csv')
            list_df.to_csv(str(file_path))
        
        if not list_df.empty:
        
            print(self.msg.success_get_my_list_data.format(
                len(list_names)))
            
            return list_df
        
        print(self.msg.error_get_my_list_data)

    def get_ids_from_names(self, source_of_members):
        
        all_are_ids = utils.members_have_ids(source_of_members)
        
        if not all_are_ids:
            member_ids = []
            for member in source_of_members:
                try:
                    user = self.API.get_user(member)
                    member_ids.append(user.id)
                except tweepy.error.TweepError:
                    print(self.msg.error_get_ids_from_names.format(member))
                
        else:
            member_ids = source_of_members
        
        return member_ids
        
    def create_list(self, name, members):

        # To do: add error handling
        # for non-existent handles/ids
        if os.path.isabs(str(members)):
            
            filename, file_ext = os.path.splitext(members)
            
            # In case members are in Excel file...
            if file_ext == '.xlsx' or file_ext == '.xls':
                # Read in first df col & convert to list
                df = pd.read_excel(members, cols='A', header=None)
                members = df.iloc[:, 0].tolist()
            else:
                # Use this to read in .csv or .txt
                members_file = open(members, 'r')
                members = members_file.read().splitlines()
                members = [member.strip('"') for member in members]
                members_file.close()
                
        if isinstance(members, list):
            # Get ids if list items are str
            member_ids = self.get_ids_from_names(members)
            
            # Create the actual list; get slug
            new_list = self.API.create_list(name)
            new_slug = new_list.slug
            
            # Log members not added
            members_not_added = []
            
            for member_id in member_ids:
                try:
                    self.API.add_list_member(user_id=member_id, slug=new_slug,
                                             owner_screen_name=self.OWNER)

                except tweepy.TweepError:
                    members_not_added.append(member_id)
                    
                    print(self.msg.error_create_list.format(member_id))
                    
                    time.sleep(60)

                    continue
                
                time.sleep(1)
                    
        else:
            raise TypeError(self.msg.error_create_list_path)
        
        ts = utils.get_timestamp()
        
        print(self.msg.success_create_list.format(
            name, ts, (len(member_ids)-len(members_not_added))))  # To do: hide if used w/i function

    def copy_list(self, owner, slug):
    
        # To do: error handling for rate limits for large lists
    
        # Get the actual list object
        list_source = self.API.get_list(owner_screen_name=owner, slug=slug)
        
        # Get the list name to copy 
        list_name = list_source.name
        
        # Get members from the list
        list_to_copy = self.get_list_members(owner, slug)
        
        # Create copy using same name
        self.create_list(list_name, list_to_copy)
        
        ts = utils.get_timestamp()
        
        print(self.msg.success_copy_list.format(
            list_name, slug, owner, ts))

    def delete_all_lists(self):
    
        list_result_set = self.API.lists_all(self.OWNER)
        list_slugs = []
        
        if len(list_result_set) > 0:
            for item in list_result_set:
                list_slugs.append(item.slug)
            for slug in list_slugs:
                self.API.destroy_list(owner_screen_name=self.OWNER, slug=slug)
                
            print(self.msg.success_delete_all_lists.format(len(list_slugs)))
            
        else:
              
            print(self.msg.error_delete_all_lists)
            
    def delete_all_tweets(self):
    
        status_counter = 0
        
        # Loop over tweets in user time-line; increment counter by one
        for status in tweepy.Cursor(self.API.user_timeline).items():
            self.API.destroy_status(status.id)
            status_counter += 1
            
        if status_counter > 0:
        
            print(self.msg.success_delete_all_tweets.format(status_counter))
        else:    
            print(self.msg.error_delete_all_tweets)
