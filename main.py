#!/usr/bin/python
# -*- coding: utf-8 -*-

# Basicos
import os
import sys
import time
import json
import platform
import random

# Modulo interno para checar o arquivo de configuracao
import cfgCheck

# Assincronicidade
import asyncio
import aiohttp

# Discord
import disnake
from disnake.ext import commands
from disnake.ext.commands import Context
from disnake import ApplicationCommandInteraction, Option, OptionType

# Database
from peewee import PeeweeException, Value
from model import BaseModel, Attack


# confere a existencia do arquivo de configuracao, config.json
config = cfgCheck.CheckCFG()

# Pega as informacoes necessarias do arquivo de configuracao,
# gerando uma cópia deles para uso interno
token = str(config["token"])[::]
prefix = str(config["prefix"])[::]

# Instancia o bot
client = commands.Bot(command_prefix=prefix)

# Decorador da instancia do bot,
# para executar uma acao asincrona quando o bot estiver pronto
@client.event
async def on_ready():
    print("< Monki Flip Bot > ja esta flipando!")


# Trata os inputs de comando
def tratarCommando(comma):
    # Pega todos os possiveis triggers,
    # utilizando as nova funcao de lista compacta do python
    triggers = [comma.command.aliases]

    command = ""

    for i in triggers:
        comma.message.content.replace(i)


# Decorador para criar um comando,
# recebendo como argumento uma lista de strings validas como trigger do comando

@client.command(aliases=["r", "roll"])
# Comando de rolar dado
# Suporda um dado padrao e dados personalizados desed sua ultima atualizacao
async def rolldice(ctx):

    # Checa se o autor de uma mensagem e o mesmo que iniciou o comando
    def check(m):
        return m.author == ctx.author

    # Confere se o comando e de um dado unico
    if ctx.message.content == "!r":

        # Lista de dados possiveis
        possibleDices = ["2", "4", "6", "8", "10", "12", "20"]

        # Variavel para armazenar os dados escolhidos
        x = ""

        # Gera uma embed:
        embed = disnake.Embed(
            # Titulo recebe um emoji externo
            title="**Escolha um dado <:1d6:923239505610309632>**",
            # Usando lista compactada, juntamente com .join(),
            # para gerar de forma escalavel uma string,
            # com todos os possiveis dados, separados com uma virgula
            description=f"{', '.join([x for x in possibleDices])}",  
            color=0x9C84EF,  # Cor da barra lateral
        )

        # Adiciona um footer para a instancia da embed
        embed.set_footer(text=f"A pedido de:  {ctx.author.display_name}")

        # Manda a mensagem (nesse caso apenas o embed) de forma asincrona
        message = await ctx.send(embed=embed)

        # Faz uma tentativa onde se espera 10s para uma resposta
        try:
            message = await client.wait_for(
                "message",
                check=check,
                timeout=10.0)

            m = message.content

            # Caso a resposta nao esteja na lista de dados possiveis,
            # vai retornar um embed dizendo que ele nao e um dado valido
            if m not in possibleDices:

                # Instancia o embed
                embed = disnake.Embed(
                    title="**Dado invalido !**",
                    color=0xEF9C84)

                # Retorna no footer quem pediu aquele comando,
                # para nao gerar confusao caso mais de um jogador execute o comando
                embed.set_footer(
                    text=f"A pedido de:  {ctx.author.display_name}")

                # Adiciona um campo com uma lista dos possiveis dados como sugestao
                embed.add_field(
                    name=f"Tente com um dos dados a seguir : {', '.join([x for x in possibleDices])}",
                    value="Ou use o comando no formato: !r XdY",
                    inline=False,
                )

                # Manda esse embed gerado
                message = await ctx.send(embed=embed)

            # Caso a resposta  esteja na lista de dados possiveis:
            if m in possibleDices:

                # Instancia da embed
                embed = disnake.Embed(
                    title="**🎲 Rolagem de dados 🎲**",
                    description=f"Rolagem de:  {m}",
                    color=0x84EF9C,
                )

                # Adiciona um campo de resultado e gera um dado aleatório de (0,m]
                embed.add_field(
                    name="Resultado:",
                    value=str(random.randint(1, int(m))),
                    inline=False,
                )

                # Retorna no footer quem pediu aquele comando,
                # para nao gerar confusao caso mais de um jogador execute o comando
                embed.set_footer(text=f"A pedido de:  {ctx.author.display_name}")

                # Manda esse embed gerado
                message = await ctx.send(embed=embed)

        # Caso de asyncio.TimeoutError na espera de 10s,
        # ou seja, caso o usuario nao responda
        except asyncio.TimeoutError:

            # Instancia um embed
            embed = disnake.Embed(
                title="**Cancelado**",
                description=f"O autor do comando demorou mais de 10 segundos para responder",
                color=0xEF9C84,
            )

            # Adicionando um footer, com o usuario que requisitou esse comando que expirou
            embed.set_footer(text=f"A pedido de:  {ctx.author.display_name}")

            # E envia
            await message.edit(embed=embed)

    # Caso o comando nao seja de um dado unico, e na lista dos dados default
    # no caso os inputs que cairiam aqui seriam os do tipo:
    # 1d19, 3d14 etc
    else:
        a = str(ctx.message.content).replace("!r ", "")
        # Da o split no comando, mais especificamente no 'd'
        # ou seja de '3d14' teremos uma lista '[3,14]' que pode ser usada como
        # Quantos dados e m em (0,m]
        b = a.split("d")

        # Caso algo de errado
        if a == b:
            await ctx.send("Algo de errado nao esta certo, tente novamente.")

        else:
            # Lista onde os resultados dos dados personalizados ficarao armazenados
            resultadosPersonalizados = []

            # Roda o dado personalizado, com b[0] sendo quantas vezes um dado de (0,m] sera rodado
            for i in range(int(b[0])):
                resultadosPersonalizados.append(str(random.randint(1, int(b[1]))))

            # Converte a lista para uma string, separando os resultados por virgula
            ResultadoDadoPersonalizado = (
                f"{', '.join([x for x in resultadosPersonalizados])}"
            )

            # Soma dos dados personalizados
            SomaDadosPersonalizados = str(sum([int(x) for x in resultadosPersonalizados]))

            # Instancia uma embed
            embed = disnake.Embed(
                title="**🎲 Rolagem de dados 🎲**",
                description=f"{ctx.message.content}",
                color=0x84EF9C
            )

            # Adiciona um footer com o autor do comando
            embed.set_footer(text=f"A pedido de:  {ctx.author.display_name}")

            # Apenas para fins de sintaxe, verificando se dever ser resultado ou Resultados
            if len(resultadosPersonalizados) > 1:
                resultadoSyntax = "Resultados:"
            else:
                resultadoSyntax = "Resultado:"

            # Adiciona um campo com os resutados
            embed.add_field(
                name= resultadoSyntax,
                value=ResultadoDadoPersonalizado
            )

            embed.add_field(
                name="Soma:",
                value=SomaDadosPersonalizados
            )


            # Manda esse embed gerado
            await ctx.send(embed=embed)


# Decorador para criar um comando,
# recebendo como argumento uma lista de strings validas como trigger do comando
# Comando de adicionar habilidades
@client.command(aliases=["aa"])
async def addAbility(ctx, name, *, arg):

    # Faz uma checagem se ja existe um ataque com esse nome,
    # e retorna erro se ja existir
    if (
        len(
            Attack.select().where(
                Attack.username == f"{ctx.author.id}" and Attack.name == name
            )
        ) >= 1 ):
        await ctx.send(f"Ocorreu um erro criando um ataque!")

    # Caso nada de erro, adiciona o ataque no banco de dados,
    # atrelado com o autor do comando
    else:
        aux = Attack(username=f"{ctx.author.id}",
                     name=name,
                     attack=f"{arg}")
        aux.save()
        # Retorna uma mensagem sinalizando que deu tudo certo
        await ctx.send(f"Ataque {name} foi criado!")


# Decorador para criar um comando,
# recebendo como argumento uma lista de strings validas como trigger do comando
# Comando de listar habilidades
@client.command(aliases=["la"])
async def listAbility(ctx):

    # Se o usuario tiver a lista de ataques()
    if len(Attack.select().where(Attack.username == f"{ctx.author.id}")) > 0:

        # Instancia uma embed
        embed = disnake.Embed(title="A lista de ataque é", color=0xFF0000)

        # Adiciona os ataques, selecionando eles no banco de dados
        for attack in Attack.select().where(Attack.username == f"{ctx.author.id}"):
            embed.add_field(
                name=f"> {attack.name}", value=f"{attack.attack}", inline=False
            )

        # Adiciona um footer com o autor do comando
        embed.set_footer(text=f"A pedido de:  {ctx.author.display_name}")

        # E envia o embed
        await ctx.send(embed=embed)

    # Se ele nao tiver nenhum ataque,
    # envia uma mensagem sinalizando que o usuario nao possui nenhum ataque,
    # sugerindo o uso do comando que cria ataques
    else:
        # Instancia uma embed
        embed = disnake.Embed(title="Sua lista esta vazia ...", color=0xFF0000)

        # Adiciona um footer, dessa vez sugerindo o comando de adicionar ataque
        embed.set_footer(text=f"Use o comando `!aa` para adicionar um ataque aqui")

        # E envia o embed
        await ctx.send(embed=embed)


# Decorador para criar um comando,
# recebendo como argumento uma lista de strings validas como trigger do comando
# Comando para usar habilidades
@client.command(aliases=["a"])
async def Ability(ctx, name):

    # Cehca se o usuario tem aquela habilidade
    if (
        len(
            Attack.select().where(
                Attack.username == f"{ctx.author.id}" and Attack.name == name
            )
        ) >= 1):
        for attack in Attack.select().where(
            Attack.username == f"{ctx.author.id}" and Attack.name == name
        ):
            # Gera a embed dando a descricao do ataque
            embed = disnake.Embed(
                title=f"{attack.name}", description=f"{attack.attack}", color=0xFF0000
            )

    else:
        # Gera uma embed de erro caso aconteca alguem erro usando a habillidade
        embed = disnake.Embed(
            title=f"{name}",
            description=f"Ocorreu um erro usando esta habilidade!",
            color=0xFF0000,
        )

    # Envia o embed gerado
    await ctx.send(embed=embed)


# Decorador para criar um comando,
# recebendo como argumento uma lista de strings validas como trigger do comando
# Comando para remover uma habilidade
@client.command(aliases=["ra"])
async def removeAbility(ctx, name):
    # Checa se o autor do comando possui habilidades
    if (
        len(
            Attack.select().where(
                Attack.username == f"{ctx.author.id}" and Attack.name == name
            )
        ) >= 1 ):
        # Gera uma query para deletar a habilidade x do usuario y
        query = Attack.delete().where(
            Attack.username == f"{ctx.author.id}" and Attack.name == name
        )
        # Executa a query
        query.execute()

        # Instancia uma embed, dizendo que deu tudo certo e a habilidade foi removida
        embed = disnake.Embed(
            title=f"{name}",
            description=f"Habilidade Removida!",
            color=0xFF0000
        )

    else:
        # Instancia uma embed, dizendo que deu algo errado
        embed = disnake.Embed(
            title=f"{name}",
            description=f"Ocorreu um erro removendo sua habilidade!",
            color=0xFF0000,
        )

    # Envia a embed
    await ctx.send(embed=embed)


# Roda a instancia do bot, com seu respectivo token
client.run(token)