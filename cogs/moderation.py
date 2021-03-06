import discord
from discord.ext import commands
from discord.utils import get
import asyncpg

class Moderation(commands.Cog):
    """Server moderation. Such as Kick, Ban, Mute."""
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member:discord.Member, * , reason='Unspecified'):
        """Kicks someone. Requires kick members permission."""
        
        try:
            await member.kick(reason=reason)
            await ctx.send(f'**{member.name}** has been kicked.')
        except:
        	await ctx.send(f"I dont have permissions to kick {member.name}")
    
    
    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member:discord.Member,* , reason='Unspecified'):
        """Bans someone. Requires ban members permission"""
        
        try:
        	await member.ban(reason=reason)
        	await ctx.send(f'**{member.name} has been Banned**')
        except:
        	await ctx.send(f"I dont have permissions to kick {member.name}")
    
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member:discord.Member, *, reason='Unspecified'):
        """Mute someone. Requires manage roles permission. Also setup warning role first in server config."""

        res =await self.client.pgdb.fetchrow("SELECT * FROM guilddata WHERE guildid= $1", ctx.guild.id)
        wnr = res['wnr']
        
        if member != None:
            embed = discord.Embed(colour=ctx.author.color,description=f"{member.name} muted for {reason}")
            embed.set_author(name=f"{member.name}", icon_url=member.avatar_url)
            embed.set_thumbnail(url=member.avatar_url)
            role = get(ctx.guild.roles, id=wnr)
            
            if role is None:
            	return await ctx.send(f"Warning role not configured. Do `{ctx.prefix}config warningrole @role` to make a role warning role. Most probabely its the `Muted` role.")
            
            if role is not None:
            	try:
            		await member.add_roles(role)
            		await ctx.send(embed=embed)
            	except:
            		return await ctx.send(f"Cannot unmute {str(member)}. I'am missing permissions.")
            else:
            	await ctx.send("Please setup a warning role! See `help config`")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member:discord.Member):
        """Unmutes a muted member"""
        
        res =await self.client.pgdb.fetchrow("SELECT * FROM guilddata WHERE guildid= $1", ctx.guild.id)
        wnr = res['wnr']
        if member != None:
            embed = discord.Embed(colour=ctx.author.color,description=f"{member.name} Unmuted")
            embed.set_author(name=f"{member.name}", icon_url=member.avatar_url)
            embed.set_thumbnail(url=member.avatar_url)
            role = get(ctx.guild.roles, id=wnr)
            
            if role is None:
            	return await ctx.send(f"Warning role not configured. Do `{ctx.prefix}config warningrole @role` to make a role warning role. Most probabely its the `Muted` role.")
            
            can = False
            for r in member.roles:
            	if r == role:
            		can = True
            		break
            if can:
            	try:
            		await member.remove_roles(role)
            		await ctx.send(embed=embed)
            	except:
            		return await ctx.send(f"Cannot unmute {str(member)}. I'am missing permissions.")
            else:
            	await ctx.send("Already unmuted")
            	
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member:discord.Member,  role:discord.Role):
        """Give someone a role."""
        
        already = False
        for mrole in member.roles:
            if role == mrole:
                already = True
                break
            else:
            	pass
        if already == False:
            try:
        	    await member.add_roles(role)
        	    embed = discord.Embed(colour=ctx.author.color)
        	    embed.set_author(name=f"{member.name}", icon_url=member.avatar_url)
        	    embed.add_field(name="__Role Added__",value=f"Member : {member.mention} \nRole : {role.mention}")
        	    embed.set_footer(text=f"Role updated by - {ctx.author.name}")
        	    await ctx.send(embed=embed)
            except:
        	    await ctx.send("⛔ Missing manage roles permission or this role is higher than my role")
        else:
        	await ctx.send(f"🐸 {member.name} already has the role!")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, member:discord.Member,  role:discord.Role):
        """Remove a role from someone"""

        already = False
        for mrole in member.roles:
            if role == mrole:
                already = True
                break
            else:
            	pass
        if already:
            try:
        	    await member.remove_roles(role)
        	    embed = discord.Embed(colour=ctx.author.color)
        	    embed.set_author(name=f"{member.name}", icon_url=member.avatar_url)
        	    embed.add_field(name="__Role Removed__",value=f"Member : {member.mention} \nRole : {role.mention}")
        	    embed.set_footer(text=f"Role updated by - {ctx.author.name}")
        	    await ctx.send(embed=embed)
            except:
        	    await ctx.send("⛔ Missing manage roles permission or this role is higher than me")
        else:
        	await ctx.send(f"🙄 Don't be silly! {member.name} doesn't have the role!")

def setup(client):
    client.add_cog(Moderation(client))
