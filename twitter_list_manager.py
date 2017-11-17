from datetime import datetime
import pandas as pd
import tweepy 
import json
import time
import csv
import os

auth_dict = {
    'CONSUMER_KEY': os.environ.get('CONSUMER_KEY'),
    'CONSUMER_SECRET': os.environ.get('CONSUMER_SECRET'),
    'ACCESS_TOKEN': os.environ.get('ACCESS_TOKEN'),
    'ACCESS_TOKEN_SECRET': os.environ.get('ACCESS_TOKEN_SECRET'),
    'OWNER': os.environ.get('OWNER'),
    'OWNER_ID': os.environ.get('OWNER_ID')
}

path_error_msg = "The argument 'members = ' must contain either a list object or an absolute path to a file containing list of members."

class TwitterListManager:
    
    def __init__(self):
        
        auth = tweepy.OAuthHandler(
            auth_dict['CONSUMER_KEY'],
            auth_dict['CONSUMER_SECRET'])
            
        auth.set_access_token(
            auth_dict['ACCESS_TOKEN'],
            auth_dict['ACCESS_TOKEN_SECRET'])
        
        global OWNER 
        OWNER = auth_dict['OWNER']
        
        global OWNER_ID 
        OWNER_ID = auth_dict['OWNER_ID']
        
        global API
        API = tweepy.API(auth)
    
    def post_tweet(self,text):

        API.update_status(status=text)
        
        current_time = time.time()
        current_time_stamp = datetime.fromtimestamp(
            current_time).strftime('%Y-%m-%d %H:%M:%S')
            
        print("Success! You tweeted '{}' on {}.".format(text,current_time_stamp))

    def get_list_members(self,owner,slug,attr='screen_name'):
    
        output_list = []
        
        for member in tweepy.Cursor(API.list_members,owner,slug).items():
            if attr == 'id':
                output_list.append(member.id)
            else:
                output_list.append(member.screen_name)
        
        return output_list

    def get_list_member_data(self,owner,slug,export=False):
        
        # Initiate empty df
        member_df = pd.DataFrame()
        
        for member in tweepy.Cursor(API.list_members,owner,slug).items():
            # Create json string from User object
            member_json_str = json.dumps(member._json)
            # Read json into line as pandas df
            member_df_row = pd.read_json(member_json_str,lines=True)
            # Append each line into member_df
            member_df = member_df.append(member_df_row)
            # To do: write output to csv instead of a df
        if export:
            filepath = os.getcwd() + '\\exports\\'
            filename = owner + '-' + slug + '-list.csv'
            member_df.to_csv(filepath + filename, index=False)
            
        return member_df

    def get_owner_lists(self,owner):
        list_result_set = API.lists_all(owner)
        list_names = []
        for item in list_result_set:
            list_names.append(item.name)
        return list_names

    def get_owner_list_data(self,owner,export=False):
        list_result_set = API.lists_all(owner)
        
        # Create fields
        list_names = []
        full_name = []
        description = []
        subscriber_count = []
        members_count = []
        created_at = []
        
        # To do: write to csv instead of a df
        
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
            filepath = os.getcwd() + '\\exports\\'
            filename = owner + '-data.csv'
            list_df.to_csv(filepath + filename, index=False)
        
        return list_df

    def get_my_lists(self):
        list_result_set = API.lists_all(OWNER)
        list_names = []
        for item in list_result_set:
            list_names.append(item.name)
            
        return list_names

    def get_my_list_data(self,export=False):
        list_result_set = API.lists_all(OWNER)
        
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
            filepath = os.getcwd() + '\\exports\\'
            filename = OWNER + '-list-data.csv'
            list_df.to_csv(filepath + filename, index=False)
            
        return list_df

    def members_have_ids(self,source_of_members):
        
        all_are_ids = all(isinstance(member,int) for member in source_of_members)
        
        return all_are_ids

    def get_ids_from_names(self,source_of_members):
        
        all_are_ids = self.members_have_ids(source_of_members)
        
        if not all_are_ids:
            member_ids = []
            for member in source_of_members:
                user = API.get_user(member)
                member_ids.append(user.id)
        else:
            member_ids = source_of_members
        
        return member_ids
        
    def create_list(self,name,members):

        # To do: add error handling
        # for non-existent handles/ids
        if os.path.isabs(str(members)):
            members_file = open(members,'r')
            members = members_file.read().splitlines()
            
        if isinstance(members,list):
            # Get ids if list items are str
            member_ids = self.get_ids_from_names(members)
            
            # Create the actual list; get slug
            new_list = API.create_list(name)
            new_slug = new_list.slug
            
            for member_id in member_ids:
                API.add_list_member(user_id = member_id, slug= new_slug, 
                                    owner_screen_name = OWNER)
        else:
            raise TypeError(path_error_msg)

    def copy_list(self,owner,slug):
    
        # To do: error handling for rate limits for large lists
    
        # Get the actual list object
        list_source = API.get_list(owner_screen_name=owner,slug=slug)
        
        # Get the list name to copy 
        list_name = list_source.name
        
        # Get members from the list
        list_to_copy = self.get_list_members(owner,slug)  
        
        # Create copy using same name
        self.create_list(list_name,list_to_copy)
        
        current_time = time.time()
        current_time_stamp = datetime.fromtimestamp(
            current_time).strftime('%Y-%m-%d %H:%M:%S')
        
        print("List '{}' with slug '{}' copied from @{} on {}.".format(
            list_name,slug,owner,current_time_stamp))

    def delete_all_lists(self):
    
        list_result_set = API.lists_all(OWNER)
        list_slugs = []
        
        if len(list_result_set) > 0:
            for item in list_result_set:
                list_slugs.append(item.slug)
            for slug in list_slugs:
                API.destroy_list(owner_screen_name=OWNER,slug=slug)
                
            print("All {} of your lists have been deleted.".format(len(list_slugs)))
            
        else:
            print("You don't have any lists to delete.")