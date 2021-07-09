# -*- coding: utf-8 -*-
import datetime
import re
import urllib.parse

import scrapy


from ouv.items import ImovelItem


def ajuste_link(value):
    return urllib.parse.urljoin('http://www.vivareal.com.br', value)

# Uso: scrapy crawl vivareal -a cidade=bh
class VivarealCrawl(scrapy.Spider):
    name = 'vivareal'
    allowed_domains = ['www.vivareal.com.br']

    def __init__(self, *args, **kwargs):
        super(VivarealCrawl, self).__init__(*args, **kwargs)
        arg_cidade = kwargs.get('cidade')
        url_vivareal_venda = 'https://www.vivareal.com.br/venda/'
        url_tipologia_terreno1 = '/lote-terreno_residencial/'
        url_tipologia_terreno2 = '/lote-terreno_comercial'
        url_local = 'santa-catarina/florianopolis'


        if arg_cidade is not None:
            if arg_cidade.lower() == 'bh':
                url_local = 'minas-gerais/belo-horizonte'
            elif arg_cidade.lower() == 'bel':
                url_local = 'para/belem'
            elif arg_cidade == 'sal':
                url_local='bahia/salvador'
            elif arg_cidade == 'arj':
                url_local = 'sergipe/aracaju'

        url1 = ''.join([url_vivareal_venda, url_local, url_tipologia_terreno1])
        url2 = ''.join([url_vivareal_venda, url_local, url_tipologia_terreno2])

        self.start_urls = [
            #url1
			#, # terreno residencial
            url2  # terreno comercial
        ]



    # location of json file
    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8'
        , 'FEED_FORMAT': "json"
        , 'FEED_URI': 'data/vivareal/vivareal.json'
        , 'CLOSESPIDER_PAGECOUNT': 0
		, 'CLOSERSPIDER_ITEMCOUNT': 20
		, 'CONCURRENT_REQUESTS' : 10
    }

    def parse(self, response):
        links = response.xpath(
            '//*/a[@class="property-card__content-link js-card-title"]/@href').extract()
        print(links)
        if links is not None:
            links = list(set(links))  # remove duplicatas
        for imovel in links:
            urlItem = ajuste_link(imovel)
            request = scrapy.Request(urlItem,
                                     callback=self.parse_item)
            request.meta['url'] = urlItem  # Crio um campo meta com o endereço padrão e passo para a outra página

            yield request

        # Aqui é crawling que segue a paginação
        lista_page_url = response.xpath('//*[@class="js-change-page"]/@href').extract()
        if len(lista_page_url) > 0:
            lista_page_url = re.sub('#', '/?', lista_page_url[-1])
            if lista_page_url is not None and lista_page_url != "/?pagina=":
                url_pesquisa = re.search(r'^(.*)\/', response.url)
                next_page_url = url_pesquisa.group(1) + lista_page_url
                yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_item(self, response):
        item = ImovelItem()

        item['siteorigem'] = 'Viva Real'

        item['url'] = response.meta['url']  # obtenho o campo meta passado

        item['titulo'] = response.xpath('//*[contains(@class, "description")]/h3/text()').extract_first()

        endereco = response.xpath('//*[contains(@class, "title__address js-address")]/text()').extract_first()
        if endereco is not None:
            end = re.search(r'(((.*)\s-\s)?(.*),\s)?(.*)\s-\s(\w+)', endereco)
            if end is not None:
                item['endereco'] = end.group(3)
                item['bairro'] = end.group(4)
                item['municipio'] = end.group(5)
                item['uf'] = end.group(6)

        tipo = response.xpath('//*[@class="breadcrumb__item-name js-link"]/text()').extract_first()
        if tipo is not None:
            tipo = tipo.split('/')
            if len(tipo) >= 1:
                item['tipologia'] = tipo[0]
        else:
            item['tipologia'] = None

        item['quarto'] = response.xpath(
            '//*[contains(@class, "features__item features__item--bedroom js-bedrooms")]/span[1]/text()').extract_first()

        item['anuncio'] = response.xpath(
            '//*[contains(@class, "js-property-title title")]/span[1]/text()').extract_first()

        item['banheiro'] = response.xpath(
            '//*[contains(@class, "features__item features__item--parking js-parking")]/span[1]/text()').extract_first()

        item['vaga'] = response.xpath(
            '//*[contains(@class, "js-detail-parking-spaces")]/span[1]/text()').extract_first()
        item['preco'] = response.xpath('//*[contains(@class, "price__price-info js-price-sale")]/text()').extract_first()
        item['condominio'] = response.xpath('//*[contains(@class, "js-detail-condo-price")]/text()').extract_first()
        item['area'] = response.xpath('//*[contains(@class, "features__item features__item--area js-area")]/span/text()').extract_first()
        item['anunciante'] = response.xpath(
            '//*[contains(@class, "publisher__name")]/text()').extract_first()



        telefone = response.xpath('//*[contains(@class, "phone-contact__phone--primary")]/@href').extract_first()
        if telefone is not None:
            telefone = list(set(telefone))
            telefone = [i for i in telefone if i != u'Ligar']
            item['telefone'] = "/".join(telefone).strip()
        else:
            item['telefone'] = None

        lista_descricao = response.xpath(
            '//*[@id="hbs-read-more__input--description__body"]/following-sibling::div/p/text()').extract()
        if len(lista_descricao) == 0:
            item['descricao'] = None
        else:
            item['descricao'] = " ".join(lista_descricao)

        item['andar'] = None
        suite = response.xpath(
            '//*[contains(@class, "js-detail-rooms")]/span[2]/text()').extract_first()
        if suite is not None:
            suite = re.search(r'0?(\d+)', suite)
            item['suite'] = suite.group(1)
        else:
            item['suite'] = None

        if item['descricao'] is not None:
            if item['suite'] is None:
                busca_suite = re.search(r'0?(\d+)\s?su[i|\xed\xcd]tes?', item['descricao'], re.IGNORECASE)
                if busca_suite is not None:
                    item['suite'] = busca_suite.group(1)

            andar = re.search(r'0?(\d+)[\xba|\xb0]\s?(andar|pavimento)', item['descricao'], re.IGNORECASE)
            if andar is not None:
                item['andar'] = andar.group(1)

        lista_caracteristicas = response.xpath(
            '//*[@id="hbs-read-more__input--description__body"]/following-sibling::div/*/li/text()').extract()
        if len(lista_caracteristicas) == 0:
            item['caracteristica'] = None
        else:
            item['caracteristica'] = "; ".join(lista_caracteristicas)

        lista_imagem = response.xpath('//*/div[contains(@class, "carousel js-carousel")]//img/@data-src').extract()
        if len(lista_imagem) > 0:
            item['imagemlista'] = "; ".join(lista_imagem[0:2])  # apenas 10 fotos no máximo
        else:
            item['imagemlista'] = None

        item['imagem'] = response.xpath('//*/div[contains(@class, "js-gallery-carousel")]//img/@src').extract_first()
        item['data'] = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')  # Data atual
        if item['descricao'] is not None:  # buscar data na descricao
            dt = re.search(r'(\d+/\d+/\d{4})', item['descricao'])
            if dt is not None:
                dt = dt.group(1).encode('ascii', 'ignore')
                dt = datetime.datetime.strptime(dt, '%d/%m/%Y')
                dt = datetime.datetime.strftime(dt, '%Y-%m-%d')
                item['data'] = dt

        item['urlmapa'] = None
        item['latitude'] = None
        item['longitude'] = None
        lat = response.xpath('//*/meta[contains(@property, "latitude")]/@content').extract_first()
        lon = response.xpath('//*/meta[contains(@property, "longitude")]/@content').extract_first()
        if lat is not None and lon is not None:
            item['latitude'] = lat
            item['longitude'] = lon
            # Formatação do google maps a partir da latitude e longitude
            item['urlmapa'] = "".join(['https://www.google.com/maps/search/?api=1&query='
                                          , item['latitude']
                                          , ","
                                          , item['longitude']
                                       ])
            
            
            

        # Correções
        item['codigo'] = None

        if item['tipologia'] is not None:
            if item['titulo'] is not None:
                item['titulo'] = item['titulo'].strip()
                m = re.search(r'(.*?)\s(com|\xe0)', item['titulo'])
                if m is not None:
                    item['tipologia'] = m.group(1).capitalize()
            # Caso do andar "Térreo" para apartamentos
            if item['andar'] is None and item['tipologia'] == 'Apartamento' and item['descricao'] is not None:
                andar = re.search(r'[^pavimento](.|\s)(t[\xc9\xe9e]rreo)', item['descricao'], re.IGNORECASE)
                if andar is not None:
                    item['andar'] = 0  # Térreo é ZERO

        if item['url'] is not None:
            m = re.search(r"^.*id-(\d*)\/", item['url'])
            if m is not None:
                item['codigo'] = m.group(1)

        # Ajustes
        if item['banheiro'] is not None:
            item['banheiro'] = item['banheiro'].strip()

        if item['quarto'] is not None:
            item['quarto'] = item['quarto'].strip()

        if item['suite'] is not None:
            item['suite'] = item['suite'].strip()

        if item['vaga'] is not None:
            item['vaga'] = item['vaga'].strip()

        if item['telefone'] is not None:
            item['telefone'] = item['telefone'].replace('(0', '').replace(') ', '').replace('-', '').replace(' ', '')

        if item['preco'] is not None:
            item['preco'] = item['preco'].replace('R$ ', '').replace('.', '')
            item['preco'] = item['preco'].replace(',', '.').strip()

        if item['condominio'] is not None:
            item['condominio'] = item['condominio'].replace('R$ ', '').replace('.', '')
            item['condominio'] = item['condominio'].replace(',', '.').strip()

        if item['area'] is not None:
            item['area'] = item['area'].replace('.', '')
            item['area'] = item['area'].replace(',', '.').strip()

        if item['tipologia'] == 'Lote/Terreno':
            item['tipologia'] = 'Terreno'

        yield item
        
 
  
