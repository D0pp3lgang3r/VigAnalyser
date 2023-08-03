from terminaltables import SingleTable
from colorama import Fore

HEADERS = [Fore.GREEN+"Trigram", "Appears at places", "Difference"+Fore.RESET]
alphabet = "abcdefghijklmnopqrstuvwxyz"
ALPHA_DICT = {letter: idx for idx, letter in enumerate(alphabet)}
REF_IND_CO = 0.068

def banner():
	content = f"""
__   ___        _             _                  
\ \ / (_)__ _  /_\  _ _  __ _| |_  _ ___ ___ _ _ 
 \ V /| / _` |/ _ \| ' \/ _` | | || (_-</ -_) '_|
  \_/ |_\__, /_/ \_\_||_\__,_|_|\_, /__/\___|_|  
        |___/                   |__/          
 {Fore.CYAN}[+] Author : D0pp3lgang3r{Fore.RESET}
 [+] Date : 03/08/2023   
	"""
	return content

def generate_trigrams(text):
	trigrams = [text[i:i+3] for i in range(len(text)-2)]
	return trigrams

def find_trigram_occurrences(text, trigram):
	trigram_positions = []
	trigram_length = len(trigram)

	for i in range(len(text) - trigram_length + 1):
		if text[i:i + trigram_length] == trigram:
			trigram_positions.append(i+1)
	return trigram_positions

def get_prime_factors(number):
	prime_factors = []
	d=2
	while d * d <= number:
		if number % d == 0:
			prime_factors.append(d)
			number //= d
		else:
			d+=1
	if number > 1:
		prime_factors.append(number)

	return prime_factors

def split_ciphertext(ciphertext, keylength):
	string_list = []
	s = ""
	j = 0
	while j < keylength:
		for i in range(j, len(ciphertext), keylength):
			s+=ciphertext[i]
		string_list.append(s)
		s = ""
		j+=1
	return string_list

def IndCo(string):
	# print(f"{Fore.GREEN}[+] For string : {string}{Fore.RESET}")
	
	letters_row = [" ", ]
	idx_row = ["i", ]
	frequence_row = ["Fi", ]
	
	for letter in string:
		if letter not in letters_row:
			letters_row.append(letter)
			idx_row.append(ALPHA_DICT.get(letter))
			frequence_row.append(string.count(letter))

	table_data = [letters_row, idx_row, frequence_row]
	
	# print(SingleTable(table_data).table)
	
	freq_res = sum([f_i * (f_i - 1) for f_i in frequence_row[1:]])
	indco = (1 / (len(string) * (len(string) - 1))) * freq_res
	
	return round(indco, 3)

def MutIndCo(string, shifted_string):
	letters_s = []
	f_s = [] # string frequences
	letters_t = []
	f_t = [] # shifted_string frequences
	
	for letter in string:
		if letter not in letters_s:
			letters_s.append(letter)
			f_s.append((letter, string.count(letter)))

	for letter in shifted_string:
		if letter not in letters_t:
			letters_t.append(letter)
			f_t.append((letter, shifted_string.count(letter)))

	dict_fs = dict(f_s)
	frequences = []
	for c, freq in f_t:
		if c in dict_fs:
			final = dict_fs[c]*freq
			frequences.append(final)
	result = round(sum(frequences)/(len(string)*len(shifted_string)),3)
	return result


def shift_string(string, sigma):
	return ''.join([alphabet[(ALPHA_DICT.get(c)+sigma)%len(alphabet)] for c in string])


if __name__ == '__main__':
	print(banner())
	print(f"{Fore.RED}[+] Applying Kasiski Method{Fore.RESET}")
	
	print(f"{Fore.YELLOW}[*] Enter ciphertext...{Fore.RESET}")
	ciphertext = input("[>] ")
	
	if ciphertext != "":
		
		trigrams = generate_trigrams(ciphertext)
		table_data = [HEADERS, ]
		
		for t in trigrams:
			occurences = find_trigram_occurrences(ciphertext, t)
			
			if len(occurences) >= 2:
				difference = occurences[1] - occurences[0]
				data = (t, ' and '.join([str(o) for o in occurences]), f"{difference} = {'*'.join([str(f) for f in get_prime_factors(difference)])}")
				if data not in table_data:
					table_data.append(data)

		print(SingleTable(table_data).table)
		
		keylength_list = []
		indexes_co = []
		avg_list = []
		for keylength in range(4, 13):
			strings = split_ciphertext(ciphertext, keylength)
			keylength_list.append(keylength)
			index_co = []
			for string in strings:
				index_co.append(IndCo(string))
			indexes_co.append(index_co)
			avg_list.append(round(sum(index_co) / len(index_co), 3))

		table_data = [["Key Length", "Average Index", "Individual Indices of Coincidence"]]
		closest = min(avg_list, key=lambda x: abs(x - REF_IND_CO))
		idx_closest = avg_list.index(closest)
		
		for i in range(len(indexes_co)):
			table_data.append([keylength_list[i], avg_list[i], ' '.join([str(val) for val in indexes_co[i]])])
		
		print(SingleTable(table_data).table)
		keylength=keylength_list[idx_closest]
		
		print(f"{Fore.CYAN}[+] From the above table we guess keylength is probably : {keylength}{Fore.RESET}")
		print(f"{Fore.YELLOW}[*] Enter keylength...{Fore.RESET}")
		keylength = int(input("[>] "))
		strings = split_ciphertext(ciphertext, keylength)
		
		first_table_data = [["i", "j"] + [str(_) for _ in range(len(alphabet)//2)]]
		second_table_data = [["i", "j"] + [str(_) for _ in range(len(alphabet)//2,len(alphabet))]]
		equations = [["i", "j", "Shift", "MutIndCo", "Shift Relation"]]
		
		for i in range(keylength):
			
			for j in range(i+1, keylength):
				
				row = [i+1, j+1, ]
				
				for sigma in range(len(alphabet)):
					
					si = strings[i]
					sj = strings[j]
					sj_sigma = shift_string(sj, sigma)
					value = MutIndCo(si, sj_sigma)
					
					if value >= 0.060:
						row.append(f"{Fore.GREEN}{value}{Fore.RESET}")
						row_equation = [i+1, j+1,sigma,value,f"β{j+1} = β{i+1} + {-sigma % 26}"]
						equations.append(row_equation)
					
					else:
						row.append(value)
				
				first_table_data.append(row[0:len(alphabet)//2+2])
				second_table_data.append([i+1, j+1, ]+row[len(alphabet)//2+2:len(alphabet)+2])
				row = []

		print(SingleTable(first_table_data).table)
		print(SingleTable(second_table_data).table)
		print(SingleTable(equations).table)