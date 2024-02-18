from newspaper import Article
from goose3 import Goose
from markdownify import markdownify as md
from bs4 import BeautifulSoup

import trafilatura
import xml.etree.ElementTree as ET
import datetime
import re
import requests

class ArticleParser:
    def __init__(self, url):
        self.article_data = {}
        self.response_to_markdown = ''
        self.status_code = 0
        self.title = ''
        self.description = ''
        self.keywords = []
        self.publish_date = datetime.datetime.now()
        self.newspaper_summary = ''
        self.goose_summary = ''

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',

                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',

                'Cache-Control': 'max-age=0',

                'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"macOS"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            }

            response = requests.get(url, headers=headers)
            self.status_code = response.status_code

            if response.status_code == 200:
                # Newspaper
                newspaper = Article(url)
                newspaper.download(input_html=response.text)
                newspaper.parse()
                newspaper.nlp()

                self.newspaper_summary = newspaper.text
                self.publish_date = newspaper.publish_date or datetime.datetime.now()

                # Goose
                goose = Goose()
                article = goose.extract(raw_html=response.text)

                self.title = article.title
                self.description = article.meta_description
                self.keywords = article.meta_keywords
                self.goose_summary = article.cleaned_text

                # Trafilatura
                xml_tree = trafilatura.extract(response.text, output_format='xml', include_comments=False, include_images=True)

                if xml_tree:
                    root = ET.fromstring(xml_tree)
                    self.process_xml(root)

                soup = BeautifulSoup(response.text, 'html.parser')
                meta_tag = soup.find('meta', attrs={'property': 'preview'})
                main_text = self.select_best_summary()

                if meta_tag:
                    meta_content = meta_tag.get('content')
                    meta_content_trimmed = meta_content[0:25]
                    start_index = main_text.find(meta_content_trimmed)

                    if start_index != -1:
                        main_text = main_text[start_index:]

                keywords_list = [keyword.strip() for keyword in self.keywords.split(',') if keyword.strip()]
                self.article_data = {
                    'title': self.title,
                    'description': self.description,
                    'keywords': keywords_list,
                    'summary': main_text,
                    'publish_date': self.publish_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'markdown_summary': md(self.response_to_markdown)
                }
            else:
                self.article_data = {'status_code': self.status_code, 'message': 'Failed to retrieve article.'}
        except Exception as e:
            self.article_data = {'status_code': 500, 'message': f'An error occurred: {str(e)}'}

    def process_xml(self, root):
        for child in root.iter():
            if child.tag in ['p', 'head']:
                self.response_to_markdown += f'<{child.tag}>{child.text}</{child.tag}>'
            elif child.tag == 'list':
                self.response_to_markdown += '<ul>' + ''.join(f'<li>{item.text}</li>' for item in child) + '</ul>'
            elif child.tag == 'graphic':
                self.response_to_markdown += f'<img src="{child.attrib["src"]}" alt="{child.attrib.get("alt", "")}" />'

    def select_best_summary(self):
        markdown_summary = md(self.response_to_markdown, heading_style="ATX")
        best_summary = max([self.newspaper_summary, self.goose_summary, markdown_summary], key=len)

        return re.sub(r'[\w.+-]+@[\w-]+\.[\w.-]+', 'REDACTED', best_summary)