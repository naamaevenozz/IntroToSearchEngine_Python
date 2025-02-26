import copy
import sys
import urllib.parse
import pickle
import requests
import bs4
from copy import deepcopy
import os


def crate_each_dict(base_url, relativr_url,all_links):
    """
    The function accepts a website address and a web page.
    The function returns a dictionary containing all the pages linked to the received page and the number of links.
    :param web_adress: str
    :param index_file: str
    :return:dict
    """
    links_dict = {}
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                            '(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
    full_url = urllib.parse.urljoin(base_url, relativr_url)
    # ask for permission request to access the html page
    response = requests.get(full_url, headers=header)
    # if response==200:

    my_html = response.text
    soup = bs4.BeautifulSoup(my_html, 'html.parser')
    for p in soup.find_all("p"):
        for link in p.find_all("a"):
            target = link.get("href")
            if target != "":
                if target in all_links:
                    if target in links_dict:
                        links_dict[target] += 1
                    else:
                        links_dict[target] = 1
    return links_dict


def crawl(base_url, index_file, out_file):
    """
    The function receives an address of a website, a text file containing the internet content
    of the website and the name of an output file. The function returns a dictionary detailing each web page for the pages it points to.
    In addition, the function saves the dictionary of links in the format of a pickle file
    """
    # Create dictionary to store links and their votes
    links_dict = {}
    # open the index file
    all_links=[]
    with open(index_file, "r") as f:
        lines = f.readlines()
    #create list that include all links
    for line in lines:
        current_line = line
        if "\n" in line:
            current_line = line[:-1]
        all_links.append(current_line)
    #for each link we create dict
    for line in lines:
        current_line = line
        if "\n" in line:
            current_line = line[:-1]
        links_dict[current_line] = crate_each_dict(base_url, line,all_links)
    # open file in pickle format and save the dict we create in the current pickle file.
    with open(out_file, 'wb') as f:
        pickle.dump(links_dict, f)


def reset_dict_lists(dict, value):
    """
    A function that receives a dictionary of lists and returns
    the dictionary with the same keys but resets the lists
    :param dict:
    :return: dict
    """
    new_dict = {}
    for key, _ in dict.items():
        new_dict[key] = value
    return new_dict


def page_rank(iterations, dict_file, out_file):
    """
    The function accepts a number of runs, a website and an output file name.
    The function creates a dictionary containing the web pages from the received file and its rating (votes by other pages)
    :param iterations: int
    :param dict_file: str
    :param out_file: str
    """
    # open the index file
    with open(dict_file, 'rb') as origin_dict:
        crawl_dict = pickle.load(origin_dict)

    new_r = reset_dict_lists(crawl_dict, 0)
    r = reset_dict_lists(crawl_dict, 1)
    iterations=int(iterations)
    for n in range(iterations):
        for primary_keys,second_val in crawl_dict.items():
            for inner_web,value in second_val.items():
                new_r[inner_web] += (r[primary_keys] * value) / (sum(crawl_dict[primary_keys].values()))
        r = new_r
        new_r = reset_dict_lists(new_r, 0)
    # open file in pickle format and save the dict we create in the current pickle file.
    with open(out_file, 'wb') as f:
        pickle.dump(r, f)

def extract_words_from_html(base_url, relativr_url):
    """
    The function receives an address of a web page and
    returns a list containing all the words on the page
    :param relativr_url: str
    :return: list
    """
    words_lst = []
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
    full_url = urllib.parse.urljoin(base_url, relativr_url)
    # ask for permission request to access the html page
    response = requests.get(full_url, headers=header)
    # if response==200:
    my_html = response.text
    soup = bs4.BeautifulSoup(my_html, 'html.parser')
    for p in soup.find_all("p"):
        content = p.text
        # Turn the content into a list where each element is a word
        p_list = content.split()
        # Add each word individually to the list that includes all the words on the page
        for item in p_list:
            words_lst.append(item)
    return words_lst


def file_to_dict(filename):
    """
    A function that receives a text file and takes each
    line in it and turns it into a key in the dictionary
    :param filename:str
    :return: dict
    """
    ret_dict = {}
    with open(filename, 'r') as file:
        for line in file:
            current_line = line
            if "\n" in line:
                current_line = line[:-1]
            ret_dict[current_line] = None
    return ret_dict


def add_words_as_keys(word_lst, dict, html_keys):
    """
    The function accepts a list of strings and a dictionary. The function returns the updated dictionary after adding the words
    that do not exist in it as keys to additional keys
    :return:dict
    """

    for word in word_lst:
        # To avoid creating a duplicate key, make sure the word does not exist
        if word not in dict and word != "":
            # add the word as a key with None value
            dict[word] = deepcopy(html_keys)
    return dict


def update_dict(dict, words_of_any_html):
    """
    The function receives a dictionary and a web adress in which all the keys are words whose edit is another dictionary with all the URLs.
    The function returns a table that updates each site key value according to the number of times a word appears in it.
    :param dict:dict
    :return:dict
    """
    for word, out_key in dict.items():
        for html_page, value in out_key.items():
            if "\n" in html_page:
                current_html = html_page[:-1]
            else:
                current_html = html_page
            lst_words = words_of_any_html[current_html]
            if lst_words.count(word) > 0:
                w = word
                c = current_html
                counter = lst_words.count(word)
                val = dict[word][current_html]
                dict[word][current_html] = lst_words.count(word)
    return dict

def del_none_from_dict(origin_dict):
    """
    The func delete from dict all the None values.
    :return:dict
    """
    keys_to_remove=[]
    for word, out_key in origin_dict.items():
        for html_page, value in out_key.items():
            if value==None:
                #del origin_dict[word][html_page]
                keys_to_remove.append((word,html_page))
    for key in keys_to_remove:
        del origin_dict[key[0]][key[1]]
    return origin_dict
def words_dict(base_url, index_file, out_file):
    """
    The function receives a dictionary, a file name that contains web pages and an output file name.
    The function produces a dictionary in which all the words appear and the number of times they appear on each page of the file
    :param base_url:str, web adress
    :param index_file: str, name of txt file that include all the names of html pages
    :param out_file: str,path
    """
    # Create dictionary to store links and their votes
    all_words_dict = {}
    # open the index file
    f = open(index_file)
    html_keys = file_to_dict(index_file)
    # create dict that it's keys are html pages and we will add all the words in each html in the for loop.
    words_of_any_html = html_keys.copy()
    for line in f:
        current_line = line
        if "\n" in line:
            current_line = line[:-1]
        lst_current_page = extract_words_from_html(base_url, current_line)
        # set the value of the current html with list that include all the words in this page.
        words_of_any_html[current_line] = lst_current_page
        all_words_dict = add_words_as_keys(lst_current_page, all_words_dict, html_keys)
    # close the file we read from
    f.close()
    all_words_dict = update_dict(all_words_dict, words_of_any_html)
    all_words_dict=del_none_from_dict(all_words_dict)
    with open(out_file, 'wb') as f:
        pickle.dump(all_words_dict, f)


def sort_top_from_dict(dict):
    """
    get the rank dict and return it sorted- from the Highest to lowest
    :param dict:
    :return:
    """
    sort_dict=list(sorted(dict.items(),key=lambda x: x[1],reverse=True))
    return sort_dict

def sortted_max_result(dict,max_result):
    """
    The function sorts the max_results from the dictionary and returns a list of them.
    :param dict: dict
    :param max_result: int
    :return: list
    """
    ret_lst=[]
    for i in range(max_result):
        ret_lst.append(dict[i])
    return ret_lst

def filter_rank_dict_entries(rank_dict,copy_rank_dict):
    """
    Create a new dictionary containing only the filtered entries from rank_dict
    """
    new_ret_dict={}
    for j in rank_dict:
        if j in copy_rank_dict:
            new_ret_dict[j]=rank_dict[j]
    return new_ret_dict

def check_dict(ranking_dict_file,word_dict_file):
    """
    A function that checks edge cases for empty dictionaries.
    :param ranking_dict_file: str
    :param word_dict_file: str
    :return:dict,dict
    """
    # Check if ranking_dict_file is empty
    if os.path.getsize(ranking_dict_file) == 0:
        rank_dict = {}
    # If there is a contant in the file we can export it a variable
    else:
        with open(ranking_dict_file, 'rb') as f:
            rank_dict = pickle.load(f)
    # Check if word_dict_file is empty
    if os.path.getsize(word_dict_file) == 0:
        word_dict = {}
    # If there is a contant in the file we can export it a variable
    else:
        with open(word_dict_file, 'rb') as f:
            word_dict = pickle.load(f)
    return rank_dict,word_dict

def filtered_rank_dict(query,ranking_dict_file,word_dict_file):
    """
    The function filters a ranked dictionary based on a query, selecting only the words from the query that exist in a provided word dictionary and returning both the filtered ranked dictionary
    and the list of query words found in the dictionary.
    :param query:str
    :param ranking_dict_file:str
    :param word_dict_file:str
    :return:dict,list
    """
    rank_dict,word_dict=check_dict(ranking_dict_file,word_dict_file)
    # Filter the rank_dict based on the query and word_dict
    # Split the query to words
    query_splt = query.split()
    # create lst that receives the number of words in the query and returns all the words in the query that appear in the dict
    ret_lst = []
    #create copy of rank_dict so they don't vote for the same place
    copy_rank_dict=list(copy.deepcopy(rank_dict))
    # Iterate over each word in the query
    for word in query_splt:
        # Check if the word in the query exists in the word dictionary
        if word in word_dict:
            # Add the word to the list of query words found in the dictionary
                ret_lst.append(word)
                # Iterate over the copy of rank_dict and remove entries not present in the word dictionary
                for key in range(len(copy_rank_dict)-1,-1,-1):
                    if copy_rank_dict[key] not in word_dict[word]:
                        del copy_rank_dict[key]
    #Create a new dictionary containing only the filtered entries from rank_dict
    new_ret_dict=filter_rank_dict_entries(rank_dict, copy_rank_dict)
    return new_ret_dict,ret_lst

def calc_min_rank(word,dict,html_page):
    """
    A function that determines the minimum frequency
    of occurrence for a word across multiple sites.
    :param word:str
    :param dict:dict
    :param html_page:str
    :return: int
    """
    with open(dict,'rb') as f:
        current_word=pickle.load(f)
        lowest_val=current_word[word[0]][html_page]
    for w in word:
        lowest_val=min(lowest_val,current_word[w][html_page])
    return lowest_val

def search(query,ranking_dict_file,words_dict_file,max_results):
   """
    The function is a search engine. It receives a search query, a path to the rating dictionary, a tag to the dictionary of word appearances and the maximum number of results for a search.
    The function filters and ranks the results and at the end the search results will be printed
   :param query: str
   :param ranking_dict_file:str
   :param words_dict_file:str
   :param max_results:int
   """
   # Initialize an empty dictionary to store the results
   ret_result={}
   # Convert max_results to an integer
   max_results=int(max_results)
   # Filter the query and obtain the list of words found in the dictionary
   update_query=filtered_rank_dict(query,ranking_dict_file,words_dict_file)[1]
   # If there are words found in the dictionary
   if len(update_query)!=0:
       # Filter the ranking dictionary based on the query
       new_rank_dict=filtered_rank_dict(query,ranking_dict_file,words_dict_file)[0]
       # Adjust max_results if it exceeds the length of the filtered ranking dictionary
       if max_results>len(new_rank_dict):
           max_results=len(new_rank_dict)
       # Sort and select the top max_results from the filtered ranking dictionary
       max_from_rank=sortted_max_result(sort_top_from_dict(new_rank_dict),max_results)
       # Iterate over the selected results and calculate their scores
       for new_rank_dict in max_from_rank:
           # Calculate the lowest rank for the current result
           lowest_val_rank=calc_min_rank(update_query,words_dict_file,new_rank_dict[0])
           # Multiply the rank score by the lowest rank and store the result in the ret_result dictionary
           ret_result[new_rank_dict[0]]=new_rank_dict[1]*lowest_val_rank
    # Sort and print the search results
   update_new_result=sort_top_from_dict(ret_result)
   for result in update_new_result:
        print(result[0],result[1])



def main():
    if sys.argv[1] == "crawl":
        crawl(sys.argv[2], sys.argv[3], sys.argv[4])
    if sys.argv[1] == "page_rank":
        page_rank(sys.argv[2], sys.argv[3], sys.argv[4])
    if sys.argv[1] == "words_dict":
        words_dict(sys.argv[2], sys.argv[3], sys.argv[4])
    if sys.argv[1] == "search":
     search(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])


if __name__ == "__main__":
    search("Quidditch","rank_out.pickle","word_dict.pickle",4)
    main()