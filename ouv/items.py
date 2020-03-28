# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ImovelItem(scrapy.Item):
    codigo = scrapy.Field() #identificador único do anúncio
    url = scrapy.Field() #url do anúncio
    siteorigem = scrapy.Field()
    data = scrapy.Field() #Data do registro do evento de mercado
    tipologia = scrapy.Field() #tipo do imóvel (terreno, casa, apartamento, etc)
    titulo = scrapy.Field()
    preco = scrapy.Field()
    condominio = scrapy.Field()
    area = scrapy.Field() #area do terreno
    anunciante = scrapy.Field()
    telefone = scrapy.Field()
    descricao = scrapy.Field()
    caracteristica = scrapy.Field()
    quarto = scrapy.Field()
    suite = scrapy.Field()
    banheiro = scrapy.Field()
    vaga = scrapy.Field()
    andar = scrapy.Field()
    endereco = scrapy.Field()
    bairro = scrapy.Field()
    cep = scrapy.Field()
    municipio = scrapy.Field()
    uf = scrapy.Field()
    urlmapa = scrapy.Field()
    imagem = scrapy.Field()
    imagemlista = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    atualizacao = scrapy.Field()
    anuncio = scrapy.Field() #código do anúncio ex: COD. 19667583
    #transacao = scrapy.Field() #tipo do transação do anúncio (compra, venda ou aluguel)
    #imobiliaria = scrapy.Field() #nome da imobiliária
    #iptu = scrapy.Field() #valor do iptu

    #estes campos comentados ainda não foram criados.
    #criar, colocar regra no vivareal.py e iserir o item no pipelines.py.
