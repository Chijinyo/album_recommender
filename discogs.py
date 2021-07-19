import discogs_client
from bs4 import BeautifulSoup
import requests
import numpy as np
import nltk
import re

class Discogs:
    def __init__(self):

        self.d = discogs_client.Client(
            'ExampleApplication/0.1',
            user_token="WFVHZJtqdVUWDIGFwTwuULXpOzNsZNsgxunAgtvV"
        )  # Discogs APIとの接続用変数

        print("あなたの好きなアルバムのタイトルを入力してください")
        self.serch_titile = input()
        print("そのアルバムのアーティスト名を入力してください")
        self.serch_artist = input()
        print("推薦候補アルバムの最大件数を数値で入力してください（１０以上、多ければ多いほど推薦の精度が上がりますが時間がかかりますpy）")
        self.serch_value = int(input())
        print("Please wait...")
        self.result = self.d.search(
            release_title=self.serch_titile,
            artist=self.serch_artist,
            type='master'
        )  # 入力に基づきDiscogs上で情報取得
        # self.url = self.result[0].url
        self.titles = []
        self.urls = []

        for res in self.result:
            self.titles.append(res.title.split(' - ')[1].replace(' ', '-'))

        for res in self.result:
            self.urls.append(
                R"https://www.discogs.com/master/" +
                str(res.id) +
                '-' +
                str(res.title.split(' - ')[1].replace(' ', '-').replace('(', '').replace(')', '').replace('/', '')) +
                R"/reviews?limit=250"
            )  # レビュー取得用のURL作成
        self.reviews = []

        for url in self.urls:
            self.reviews.append(
                BeautifulSoup(
                    requests.get(url).text, 'html.parser').find_all(
                    'div', class_='review_comment'
                )
            )  # レビューの取得

        # 以下73行まで形態素解析。形容詞のみを取り出す
        self.word_list = {}
        self.all_word = ''
        self.jjs = []
        for revs in self.reviews:
            for rev in revs:
                for elem in rev.contents:
                    if elem != '<br/>':
                        self.words = str(elem).split()
                        self.all_word += str(elem)
                        for word in self.words:
                            if word in self.word_list:
                                self.word_list[word] += 1
                            else:
                                self.word_list[word] = 1
        self.all_word = re.sub('https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', '', self.all_word)
        self.all_word = re.sub('br/', '', self.all_word)
        self.morph = nltk.word_tokenize(self.all_word)

        self.pos = nltk.pos_tag(self.morph)
        for elem in self.pos:
            if 'JJ' in elem:
                self.jjs.append(elem)

        # pprint.pprint(set(self.jjs))
        # pprint.pprint(sorted(self.word_list.items(), key=lambda x: x[1], reverse=True)) #単語頻度リスト

        # 入力されたアルバム情報を元に推薦アルバム候補検索
        self.result2 = self.d.search(
            year=self.result[0].main_release.year,
            genre=', '.join(self.result[0].genres),
            style=', '.join(self.result[0].styles),
            type='master'
        )

        self.result2_analysis = []
        self.i = 0

        for res in self.result2:
            if not res == self.result[0]:
                self.result2_analysis.append(self.morphological_analysis(res))  # 各アルバムのレビュー取得・形態素解析
                self.i += 1
                if self.i == self.serch_value:
                    break
        self.num_of_elem_much = []

        for res in self.result2_analysis:
            self.num_of_elem_much.append(len(set(self.jjs) & set(res)))  # 入力アルバムと推薦候補アルバムの両方のレビュー文中のに存在する形容詞の数を求める

        # 以下両レビュー内に存在する形容詞の量が多い順にアルバム情報を出力する
        A = np.array(self.num_of_elem_much)
        print('Recomended albums')
        print('------------------------------------------')
        print('1:' + self.result2[A.argsort()[len(A) - 1]].title)
        print('------------------------------------------')
        print('2:' + self.result2[A.argsort()[len(A) - 2]].title)
        print('------------------------------------------')
        print('3:' + self.result2[A.argsort()[len(A) - 3]].title)
        print('------------------------------------------')
        print('4:' + self.result2[A.argsort()[len(A) - 4]].title)
        print('------------------------------------------')
        print('5:' + self.result2[A.argsort()[len(A) - 5]].title)

    def morphological_analysis(self, result):  # レビューの形態素解析用メゾッド
        url = (
                "https://www.discogs.com/master/" +
                str(result.id) +
                '-' +
                str(result.title.split(' - ')[1].replace(' ', '-').replace('(', '').replace(')', '').replace('/', '')) +
                "/reviews?limit=250"
        )
        reviews = []
        reviews.append(
            BeautifulSoup(
                requests.get(url).text, 'html.parser').find_all(
                'div', class_='review_comment'
            )
        )

        word_list = {}
        all_word = ''
        jjs = []
        for review in reviews:
            for rev in review:
                for elem in rev.contents:
                    if elem != '<br/>':
                        words = str(elem).split()
                        all_word += str(elem)
                        for word in words:
                            if word in word_list:
                                word_list[word] += 1
                            else:
                                word_list[word] = 1
        all_word = re.sub('https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', '', all_word)
        all_word = re.sub('br/', '', all_word)
        morph = nltk.word_tokenize(all_word)

        pos = nltk.pos_tag(morph)
        for elem in pos:
            if 'JJ' in elem:
                jjs.append(elem)
        return jjs


Discogs()
