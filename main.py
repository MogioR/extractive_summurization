import re
from GoogleApi.google_sheets_api import GoogleSheetsApi
from transformers import *
from summarizer import Summarizer

# Load model, model config and tokenizer via Transformers
custom_config = AutoConfig.from_pretrained('cointegrated/rubert-tiny')
custom_config.output_hidden_states=True
custom_tokenizer = AutoTokenizer.from_pretrained('cointegrated/rubert-tiny')
custom_model = AutoModel.from_pretrained('cointegrated/rubert-tiny', config=custom_config)

model = Summarizer(custom_model=custom_model, custom_tokenizer=custom_tokenizer)


sheets = GoogleSheetsApi('google_token.json')
DOCUMENT_ID = '1PLVM0mynxt5hbwl_2FWSLWunjRf6KIzeVuYaS5GmNNo'
LIST_ID = 'Лист1'

data = sheets.get_data_from_sheets(DOCUMENT_ID, LIST_ID, 'A2',
                                   'E' + str(sheets.get_list_size(DOCUMENT_ID, LIST_ID)[1]),
                                   'ROWS')

results = []
cropped = []

for row in data:
    base = None
    ratio = None
    min_length = None
    max_length = None
    num_sentences = None

    if len(row) > 0:
        base = str(row[0])
        if len(row) > 1:
            if len(row[1]) > 0:
                ratio = float(int(row[1])/100)
            if len(row) > 2:
                if len(row[2]) > 0:
                    min_length = int(row[2])
                if len(row) > 3:
                    if len(row[3]) > 0:
                        max_length = int(row[3])
                    if len(row) > 4:
                        if len(row[4]) > 0:
                            num_sentences = int(row[4])

    if base is not None:
        params = {
            'body': base
        }
        if ratio is not None:
            params.update({'ratio': ratio})
        if min_length is not None:
            params.update({'min_length': min_length})
        if max_length is not None:
            params.update({'max_length': max_length})
        if num_sentences is not None:
            params.update({'num_sentences': num_sentences})

        result = model(**params)
        full = ''.join(result)
        results.append(full)

        buf1 = re.split(r'\.|\?|\!', base)
        buf2 = re.split(r'\.|\?|\!', full)

        buf1 = list(map(str.strip, buf1))
        buf2 = list(map(str.strip, buf2))

        buf3 = [sentence for sentence in buf1 if sentence not in buf2]

        crop = ''
        for sentence in buf3:
            crop += sentence
            if base.find(sentence) + len(sentence) < len(base):
                crop += base[base.find(sentence) + len(sentence)]
            crop += ' '

        cropped.append(crop)

sheets.put_column_to_sheets(DOCUMENT_ID, LIST_ID, 'F', 2, results)
sheets.put_column_to_sheets(DOCUMENT_ID, LIST_ID, 'G', 2, cropped)
