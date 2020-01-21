# -*- coding: utf-8 -*-
import scrapy


class TncItem(scrapy.Item):
    province = scrapy.Field()
    city = scrapy.Field()
    address = scrapy.Field()
    name = scrapy.Field()
    linkman = scrapy.Field()
    phone = scrapy.Field()
    businessmodel = scrapy.Field()
    BSBusinessScope = scrapy.Field()
    intro = scrapy.Field()
    mainproduct = scrapy.Field()
    personenterprises = scrapy.Field()
    link = scrapy.Field()
    category = scrapy.Field()
    tag = scrapy.Field()
    fax = scrapy.Field()
    businesslicense = scrapy.Field()
    certificationenterprise = scrapy.Field()
    info = scrapy.Field()
    registeredcapital = scrapy.Field()
    businessstartedin = scrapy.Field()
    BSOperatingPeriod = scrapy.Field()
    BSCreditCode = scrapy.Field()
    registerOffice = scrapy.Field()
