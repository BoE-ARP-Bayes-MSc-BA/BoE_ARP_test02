# %%
import pandas as pd
import re

# %%
def cleaning_text(contents):
    # change the text input to df
    df = pd.DataFrame(contents)
    # remove the unnessary string
    df[0] = df[0].str.replace('\n','')
    df[0] = df[0].str.replace('Bloomberg Transcript','')
    df[0] = df[0].str.replace('\x0c\n','')
    df[0] = df[0].str.replace('FINAL','')
    df[0] = df[0].str.replace('A - ','')
    df[0] = df[0].str.replace('Q - ','')
    # using re to remove the unnessary string
    def drop_unnessary(x):
        page = re.findall(r'Page \d+ of \d+', x) # 'page ... of ... '
        BIO = re.findall(r'{BIO', x) # '{BIO 18731996 <GO>}'
        Company_Name = re.findall(r'Company N ame:', x) # 'Company N ame: H annover Rueck SE'
        Company_Ticker = re.findall(r'Company Ticker:', x) # 'Company Ticker: H N R1 GR Equity'
        Date = re.findall(r'Date:', x) # Date: 2015-03-10
        if page == [] and BIO == [] and Company_Name == [] and Company_Ticker == [] and Date == []:
            return True
        else:
            return False

    true_false = df[0].apply(lambda x: drop_unnessary(x))
    df = df[true_false]

    # drop the final page declaration
    df = df[df[0] != 'This transcript may not be 100 percent accurate and may contain misspellings and other']
    df = df[df[0] != 'inaccuracies. This transcript is provided "as is", without express or implied warranties of']
    df = df[df[0] != 'any kind. Bloomberg retains all rights to this transcript and provides it solely for your']
    df = df[df[0] != 'personal, non-commercial use. Bloomberg, its suppliers and third-party agents shall']
    df = df[df[0] != 'have no liability for errors in this transcript or for lost profits, losses, or direct, indirect,']
    df = df[df[0] != 'incidental, consequential, special or punitive damages in connection with the']
    df = df[df[0] != 'furnishing, performance or use of such transcript. Neither the information nor any']
    df = df[df[0] != 'opinion expressed in this transcript constitutes a solicitation of the purchase or sale of']
    df = df[df[0] != 'securities or commodities. Any opinion expressed in the transcript does not necessarily']
    # df = df[df[0] != 'reflect the views of Bloomberg LP. ¬© COPYRIGHT 2022, BLOOMBERG LP. All rights']  # we will need this to identify the last participant
    df = df[df[0] != 'reserved. Any reproduction, redistribution or retransmission is expressly prohibited.']
    # ¬© could not be identified, would apply re
    def drop_Bloomberg_mark(x):
        Bloomberg_mark = re.findall(r'reflect the views of Bloomberg LP', x) # 'reflect the views of Bloomberg LP. ¬© COPYRIGHT 2022, BLOOMBERG LP. All rights'
        if Bloomberg_mark == []:
            return True
        else:
            return False

    true_false = df[0].apply(lambda x: drop_Bloomberg_mark(x))
    df = df[true_false]

    # drop the empthy row
    df = df[df[0] != '']
    df = df[df[0] != '']

    # reset the index to make sure the index is continuous for better processing
    df = df.reset_index(drop=True)
    
    return df
# %%
def sentence_df(df_clean_na, concat_df, company_paticipants_list, other_paticipants_list):
    no_par_df = pd.DataFrame()
    # identify the len before NaN of each column
    for column in df_clean_na.columns:
        # exclude the row if no_par_df[column]==no_par_df[f"participants_{column}"]
        no_par_df = concat_df[concat_df[column] != concat_df[f"participants_{column}"]]

    # use len(no_par_df.columns.to_list()) to write a for loop
    model_df = pd.DataFrame()
    for i in range(int(len(no_par_df.columns.to_list())/2)):
        tmp_df = pd.DataFrame()
        tmp_df = no_par_df.iloc[:,(i*2):(i*2)+2].copy()
        # extract the index as column from the text
        tmp_df['file_name'] = tmp_df.columns.to_list()[0]
        # extract the date from the index column
        tmp_df['date'] = tmp_df['file_name'].apply(lambda x: x.split('_')[0])
        # change the date column to datetime
        tmp_df['date'] = pd.to_datetime(tmp_df['date'])
        # rename to be consistent with the column name
        tmp_df.columns = ["sentence", "participants", "file_name","date"]
        # if the 'participants' column's value equals to any of the company_paticipants_list, other_paticipants_list, then set the value to 0
        tmp_df['company_paticipants_yes'] = tmp_df['participants'].apply(lambda x: 1 if x in company_paticipants_list else 0)
        tmp_df['other_paticipants_yes'] = tmp_df['participants'].apply(lambda x: 1 if x in other_paticipants_list else 0)
        # drop the row if the column "sentence" is NaN
        tmp_df = tmp_df.dropna(subset=['sentence'], how='all')
        tmp_df['company_name1']  = tmp_df['file_name'].apply(lambda x: x.split('_')[1])
        tmp_df['company_name2']  = tmp_df['file_name'].apply(lambda x: x.split('_')[2])
        tmp_df['company_name'] = tmp_df["company_name1"] + " " + tmp_df["company_name2"]
        # drop the 'company_name1' and 'company_name2' column
        tmp_df = tmp_df.drop(columns=['company_name1', 'company_name2'])
        model_df = model_df.append(tmp_df)
        return model_df
# %%
