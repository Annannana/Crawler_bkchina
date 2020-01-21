# -*- coding: utf-8 -*-
import re
import scrapy

from tnc.items import TncItem
from tnc.categories import categories


class ClothesSpider(scrapy.Spider):
    name = 'clothes'
    allowed_domains = ['tnc.com.cn']

    def start_requests(self):
        for couple in categories:
            cloth = couple[0]
            clothId = str(couple[1])
            url = f"https://www.tnc.com.cn/search/company-c-{clothId}-k--p1.html"
            yield scrapy.Request(url=url, callback=self.parse,
                                 meta={'couple': list((cloth, clothId)), 'page': 1})

    def parse(self, response):
        couple = response.meta.get('couple')
        cloth = couple[0]
        clothId = couple[1]
        page = response.meta.get('page')
        if page == 1:
            # get page number
            total_page = int(re.findall('.*?Number\((\d+)\)\;.*?', response.text)[0])
            for i in range(2, total_page + 1):
                new_url = f"https://www.tnc.com.cn/search/company-c-{clothId}-k--p{str(i)}.html"
                yield scrapy.Request(url=new_url, callback=self.parse,
                                     meta={'couple': couple, 'page': i})

        # get information on the page
        companies = response.xpath('//div[@class="result-list-company"]/ul/li')
        for company in companies:
            item = TncItem()
            item['category'] = ['纺织']
            item['tag'] = [cloth]
            item['linkman'] = company.xpath(".//font[contains(text(),'联 系 人')]/following-sibling::span/text()").get(
                '').strip()
            item['link'] = company.xpath('.//p[@class="tit"]/a[@target="_blank"]/@href').get('').strip()
            item['name'] = company.xpath('.//p[@class="tit"]/a[@target="_blank"]/text()').get('').strip()
            item["BSBusinessScope"] = company.xpath(
                './/font[contains(text(),"营业范围")]/following-sibling::span/text()').get('').strip()

            # company intro page
            intro_url = item['link'] + 'introduce.html'
            yield scrapy.Request(url=intro_url, callback=self.parse_intro,
                                 meta={'item': item})

    def parse_intro(self, response):
        item = response.meta.get('item')
        item['businessmodel'] = response.xpath("//td[contains(text(),'经营模式')]/following-sibling::td/text()").get(
            '').strip()
        item['mainproduct'] = response.xpath(
            "//div[@class='about_main']//tr//td[contains(text(),'主营产品/服务')]/following-sibling::td/text()").get(
            '').strip()
        item['address'] = response.xpath(
            "//div[@class='about_main']//tr//td[contains(text(),'详细地址')]/following-sibling::td/text()").get('').strip()
        item['intro'] = response.xpath('//div[@class="about_main"]//tr/td/p/text()').get('').strip()

        # get city and province
        area_list = response.xpath(
            "//div[@class='about_main']//tr//td[contains(text(),'所在地区')]/following-sibling::td/text()").get('').strip()
        area_list = area_list.split('-')
        if len(area_list) == 1:
            area_list = [each for each in re.sub('\r|\t| ', '', area_list[0]).split('\n') if each]
        if len(area_list) == 2 and area_list:
            item['province'] = area_list[0]
            item['city'] = area_list[1]
        elif len(area_list) >= 3 and area_list:
            item['province'] = area_list[1]
            item['city'] = area_list[2]

        # company contact page
        contact_url = item['link'] + 'contact.html'
        yield scrapy.Request(url=contact_url, callback=self.parse_contact,
                             meta={'item': item}, dont_filter=True)

    def parse_contact(self, response):
        item = response.meta.get('item')

        info = response.xpath('//meta[@name="description"]/@content').get()
        data = re.findall('.*?手机：(.*?)座机：(.*?)传真：(.*?)详细地址：.*?', info)
        if data:
            fax = data[0][-1].strip('-，')
            if fax: item['fax'] = fax
            item['phone'] = [i.strip('-，') for i in data[0][:2] if i.strip('-，')]
            linkman = re.findall('负责人：(.*?)手机：', info)
            if not item['linkman'] and linkman[0].strip('-，'): item['linkman'] = linkman[0].strip('-，')

        # company certificate page
        contact_url = item['link'] + 'certificate.html'
        yield scrapy.Request(url=contact_url, callback=self.parse_certificate,
                             meta={'item': item}, dont_filter=True)

    def parse_certificate(self, response):
        item = response.meta.get('item')
        certifications = response.xpath('//div[@class ="cert_ico fixed"]//img/@title').getall()
        for certification in certifications:
            if certification == '个人实名认证' or certification == '个体户实名认证':
                item['personenterprises'] = certification.strip()
            elif certification == '企业实名认证':
                item['certificationenterprise'] = certification.strip()

        data = response.xpath('//div[@class="cxda_info"]')
        if data:
            item['registeredcapital'] = data[0].xpath(
                './/th[contains(text(),"注册资本：")]/following-sibling::td/text()').get('').strip()
            item['businessstartedin'] = data[0].xpath(
                './/th[contains(text(),"成立日期：")]/following-sibling::td/text()').get('').strip()
            item['BSOperatingPeriod'] = data[0].xpath(
                './/th[contains(text(),"营业期限-开始：")]/following-sibling::td/text()').get('').strip()
            item['businesslicense'] = data[0].xpath(
                './/th[contains(text(),"营业执照代码：")]/following-sibling::td/text()').get('').strip()
            item['BSCreditCode'] = data[0].xpath(
                './/th[contains(text(),"注册号：")]/following-sibling::td/text()').get('').strip()
            item['registerOffice'] = data[0].xpath(
                './/th[contains(text(),"发照机关：")]/following-sibling::td/text()').get('').strip()

        yield item
