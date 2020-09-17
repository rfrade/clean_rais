# clean_rais
Clean IGBE/RAIS database

When you download the RAIS, you fave a 7z file with the year, like 2017.7z. 
If you unzip this file you get a 2017 folder. 

Set this folder in the variable path_rais in the file merge_data.py. 
Then set the path of the file campos_selecionado to the variable path_campos_selecionados and in the file campos_selecionados.config choose the fields you want.
The result will be a csv set in the variable path_base_limpa
