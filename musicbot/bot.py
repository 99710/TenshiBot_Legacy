#Github ok
#TenshiBot main code, Created by 99710 (formerly known as Harry99710)
#Uses https://github.com/Just-Some-Bots/MusicBot as a code base, music related code/commands removed
#Some code for sbooru is from EcchiBot 
#Tenshi is intended to be running on a debian linux VPS under root, certian commands may break if running on Windows/MacOS or another linux distro


import os
import sys
import time
import shlex
import shutil
import inspect
import aiohttp
import aiohttp
import discord
import asyncio
import traceback
import random
import platform
import socket
import cleverbot
import requests
import pybooru
import pixivpy3
import cleverbot_io
#import saucenaopy
import praw
import lxml
from bs4 import BeautifulSoup

#Uncomment to force pip to install/update things in requirements.txt, recomment to allow the bot to run
#import bhava-agra

bot = cleverbot_io.set(user='', key='', nick='Tenko_AI')


from discord import utils
from discord.object import Object
from discord.enums import ChannelType
from discord.voice_client import VoiceClient
from discord.ext.commands.bot import _get_variable


from io import BytesIO
from functools import wraps
from textwrap import dedent
from datetime import timedelta
from random import choice, shuffle
from collections import defaultdict

from musicbot.config import Config, ConfigDefaults
from musicbot.permissions import Permissions, PermissionsDefaults
from musicbot.utils import load_file, write_file, sane_round_int

from . import exceptions
from . import downloader
from .opus_loader import load_opus_lib
from .constants import VERSION as BOTVERSION
from .constants import DISCORD_MSG_CHAR_LIMIT, AUDIO_CACHE_PATH

from random import randint
from pybooru import Danbooru
from google_images_download import google_images_download
from pixivpy3 import *
from weather import Weather, Unit
#from saucenaopy import SauceNAO

api = AppPixivAPI()


load_opus_lib()
st = time.time()

def getID(str1):
    return str1[str1.find("id=") + 3]

def getFileURL(str1):
    first = str1.find("file_url=")
    second = str1.find('"', first+11)
    return str1[first:second]




honkhonk = [
"https://www.youtube.com/watch?v=c3vONDqvayo",
"honk honk",
"https://www.youtube.com/watch?v=-hp2d0ROK1w",
"https://youtu.be/sPaJa2QbZ0c",
"https://youtu.be/r_xeqt9l5FQ",
]

eurobeat = [
"https://www.youtube.com/watch?v=AC5PUKeYjyU", #black out
"https://www.youtube.com/watch?v=Nknem8YgM9A", #stop your self control
"https://www.youtube.com/watch?v=FS1k2CQKVAU", #remember me
"https://www.youtube.com/watch?v=fzg19RfUdJI", #heartbeat
"https://www.youtube.com/watch?v=DyGTZ5Qctpc", #set me free
"https://www.youtube.com/watch?v=P8fgaPAMq8U", #mad desire

]

dice = [
"You rolled 1",
"You rolled 2",
"You rolled 3",
"You rolled 4",
"You rolled 5",
"You rolled 6",
]

doubledice = [
"You rolled 2",
"You rolled 3",
"You rolled 4",
"You rolled 5",
"You rolled 6",
"You rolled 7",
"You rolled 8",
"You rolled 9",
"You rolled 10",
"You rolled 11",
"You rolled 12",
]

coinflip = [
"Heads!",
"Tails!",
]

fortune = [
"Hm... try asking Iku that",
"I can't say for sure",
"Maybe... :smirk:",
"Yep, 99.99% sure",
"How would you expect a Celestial to know that?",
":ok_hand:",
"Hell yea!",
"I may be a Celestial but i can safely say everything will be ok",
]

wangan = [
"pics/wangan/wangan1.png",
"pics/wangan/wangan2.png",
"pics/wangan/wangan3.png"
]

koonami = [
"This is konami's famous bemani series!",
"https://giphy.com/gifs/dUpQxRc1UPToc",
"https://s16.postimg.org/fowre5fwl/bm_money.png",
"https://giphy.com/gifs/F3V9Mrm9mDlrq",
"https://www.youtube.com/watch?v=gZMCMRU2cD0",
"https://www.youtube.com/watch?v=XH2jQNH0BtE",
]

ainsley = [
"https://giphy.com/gifs/hgtkVYPMbvCsE",
"Looks Like it's time to oil up!",
"https://giphy.com/gifs/VVQrAMo2UGgMM",
"Give your meat a good ol rubbin"
]

shitpost = [
"https://www.youtube.com/watch?v=C7fKoamz0nY",
"Touhou Hijack LOL!",
"Shitposting in this chat cuz i'm Nazrin",
"https://www.youtube.com/watch?v=7GtAad-dMS8",
"https://www.youtube.com/watch?v=iqT0iFZifgw",
]

gensokyoweather = [
"Sunny skies from here in heaven",
"How should i know? The Kappas are still installing the weather station",
"I would tell you but Marisa stole my weather station",
"Stop being lazy and look yourself",
"Peaches!",
"Dunno, weather never changes in heaven",
"Hold on, I'll ask Reimu",
"Hold on, I'll ask Nitori",
"Hold on, I'll ask Yukari",
"Raining keystones!",
]

enviromentcanada = [
"https://www.youtube.com/watch?v=fco9mR2Uzko", 
"https://www.youtube.com/watch?v=O5hGcVLwrCM",
]



class SkipState:
    def __init__(self):
        self.skippers = set()
        self.skip_msgs = set()

    @property
    def skip_count(self):
        return len(self.skippers)

    def reset(self):
        self.skippers.clear()
        self.skip_msgs.clear()

    def add_skipper(self, skipper, msg):
        self.skippers.add(skipper)
        self.skip_msgs.add(msg)
        return self.skip_count


class Response:
    def __init__(self, content, reply=False, delete_after=0):
        self.content = content
        self.reply = reply
        self.delete_after = delete_after


class MusicBot(discord.Client):
    def __init__(self, config_file=ConfigDefaults.options_file, perms_file=PermissionsDefaults.perms_file):
        self.players = {}
        self.the_voice_clients = {}
        self.locks = defaultdict(asyncio.Lock)
        self.voice_client_connect_lock = asyncio.Lock()
        self.voice_client_move_lock = asyncio.Lock()

        self.config = Config(config_file)
        self.permissions = Permissions(perms_file, grant_all=[self.config.owner_id])


        self.exit_signal = None
        self.init_ok = False
        self.cached_client_id = None


        # TODO: Do these properly
        ssd_defaults = {'last_np_msg': None, 'auto_paused': False}
        self.server_specific_data = defaultdict(lambda: dict(ssd_defaults))

        super().__init__()
        self.aiosession = aiohttp.ClientSession(loop=self.loop)
        self.http.user_agent += ' MusicBot/%s' % BOTVERSION

    # TODO: Add some sort of `denied` argument for a message to send when someone else tries to use it
    def owner_only(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Only allow the owner to use these commands
            orig_msg = _get_variable('message')

            if not orig_msg or orig_msg.author.id == self.config.owner_id:
                return await func(self, *args, **kwargs)
            else:
                #raise exceptions.PermissionsError("Owner only command", expire_in=30)
                return Response(":warning: This command can only be used my owner")
                print("[Error] User attempted to run an owner only command")

        return wrapper

    @staticmethod
    def _fixg(x, dp=2):
        return ('{:.%sf}' % dp).format(x).rstrip('0').rstrip('.')

    def _get_owner(self, voice=False):
        if voice:
            for server in self.servers:
                for channel in server.channels:
                    for m in channel.voice_members:
                        if m.id == self.config.owner_id:
                            return m
        else:
            return discord.utils.find(lambda m: m.id == self.config.owner_id, self.get_all_members())

    def _delete_old_audiocache(self, path=AUDIO_CACHE_PATH):
        try:
            shutil.rmtree(path)
            return True
        except:
            try:
                os.rename(path, path + '__')
            except:
                return False
            try:
                shutil.rmtree(path)
            except:
                os.rename(path + '__', path)
                return False

        return True




    async def update_now_playing(self, entry=None, is_paused=False):
       await self.change_presence(game=discord.Game(name='my game'))


#    async def wait_delete_msg(self, message, after):
#           await asyncio.sleep(after)
#           await self.safe_delete_message(message)

    # TODO: Check to see if I can just move this to on_message after the response check
    async def _manual_delete_check(self, message, *, quiet=False):
       if self.config.delete_invoking:
            await self.safe_delete_message(message, quiet=quiet)


    async def generate_invite_link(self, *, permissions=None, server=None):
        if not self.cached_client_id:
            appinfo = await self.application_info()
            self.cached_client_id = appinfo.id

        return discord.utils.oauth_url(self.cached_client_id, permissions=permissions, server=server)


    async def update_now_playing(self, entry=None, is_paused=False):
#        game = None

#        if self.user.bot:
#            activeplayers = sum(1 for p in self.players.values() if p.is_playing)
#            if activeplayers > 1:
#                game = discord.Game(name="music on %s servers" % activeplayers)
#                entry = None

#            elif activeplayers == 1:
#                player = discord.utils.get(self.players.values(), is_playing=True)
#                entry = player.current_entry
#
#        if entry:
 #           prefix = u'\u275A\u275A ' if is_paused else ''
#
#            name = u'{}{}'.format(prefix, entry.title)[:128]
#            game = discord.Game(name=name)
#
#        await self.change_status(game)
        await self.change_status(game=discord.Game(name='with boulders'))

    async def safe_send_message(self, dest, content, *, tts=False, expire_in=0, also_delete=None, quiet=False):
        msg = None
        try:
            msg = await self.send_message(dest, content, tts=tts)

            if msg and expire_in:
                asyncio.ensure_future(self._wait_delete_msg(msg, expire_in))

            if also_delete and isinstance(also_delete, discord.Message):
                asyncio.ensure_future(self._wait_delete_msg(also_delete, expire_in))

        except discord.Forbidden:
            if not quiet:
                self.safe_print("[Error] Failed to send message to %s, no permission" % dest.name)
#            return await self.send_message(author, ":warning: Failed to send a message due to lack of permission, ask a server admin to check permissions")
      #          self.add_reaction(message, warning)

        except discord.NotFound:
            if not quiet:
                self.safe_print("Warning: Cannot send message to %s, invalid channel?" % dest.name)

        return msg

    async def safe_delete_message(self, message, *, quiet=False):
        try:
            return await self.delete_message(message)

        except discord.Forbidden:
            if not quiet:
                self.safe_print("[Error] Cannot delete message \"%s\", no permission" % message.clean_content)

        except discord.NotFound:
            if not quiet:
                self.safe_print("[Error] Cannot delete message \"%s\", message not found" % message.clean_content)

    async def safe_edit_message(self, message, new, *, send_if_fail=False, quiet=False):
        try:
            return await self.edit_message(message, new)

        except discord.NotFound:
            if not quiet:
                self.safe_print("[Error] Cannot edit message \"%s\", message not found" % message.clean_content)
            if send_if_fail:
                if not quiet:
                    print("Sending instead")
                return await self.safe_send_message(message.channel, new)

    def safe_print(self, content, *, end='\n', flush=True):
        sys.stdout.buffer.write((content + end).encode('utf-8', 'replace'))
        if flush: sys.stdout.flush()

    async def send_typing(self, destination):
        try:
            return await super().send_typing(destination)
        except discord.Forbidden:
            if self.config.debug_mode:
                print("[Error] Could not send typing to %s, no permssion" % destination)

    async def edit_profile(self, **fields):
        if self.user.bot:
            return await super().edit_profile(**fields)
        else:
            return await super().edit_profile(self.config._password,**fields)

    def _cleanup(self):
        try:
            self.loop.run_until_complete(self.logout())
        except: # Can be ignored
            pass

        pending = asyncio.Task.all_tasks()
        gathered = asyncio.gather(*pending)

        try:
            gathered.cancel()
            self.loop.run_until_complete(gathered)
            gathered.exception()
        except: # Can be ignored
            pass

    # noinspection PyMethodOverriding
    def run(self):
        try:
            self.loop.run_until_complete(self.start(*self.config.auth))

        except discord.errors.LoginFailure:
            # Add if token, else
            raise exceptions.HelpfulError(
                "Bot cannot login, bad credentials.",
                "Fix your Email or Password or Token in the options file.  "
                "Remember that each field should be on their own line.")

        finally:
            try:
                self._cleanup()
            except Exception as e:
                print("Error in cleanup:", e)

            self.loop.close()
            if self.exit_signal:
                raise self.exit_signal

    async def logout(self):
#        await self.disconnect_all_voice_clients()
        return await super().logout()

    async def on_error(self, event, *args, **kwargs):
        ex_type, ex, stack = sys.exc_info()

        if ex_type == exceptions.HelpfulError:
            print("Exception in", event)
            print(ex.message)

            await asyncio.sleep(2)  # don't ask
            await self.logout()

        elif issubclass(ex_type, exceptions.Signal):
            self.exit_signal = ex_type
            await self.logout()

        else:
            traceback.print_exc()

    async def on_resumed(self):
        for vc in self.the_voice_clients.values():
            vc.main_ws = self.ws

    async def on_ready(self):
        print('\rTenshiBot System Initialised!')
        print('\rPosting server count...')
        requests.post('https://discordbots.org/api/bots/{}/stats'.format(self.user.id),headers={'Authorization':''}, data={'server_count':len(self.servers)})
        print('\rDone!, contiuning startup...')

        if self.config.owner_id == self.user.id:
            raise exceptions.HelpfulError(
                "Your OwnerID is incorrect or you've used the wrong credentials.",

                "The bot needs its own account to function.  "
                "The OwnerID is the id of the owner, not the bot.  "
                "Figure out which one is which and use the correct information.")

        self.init_ok = True

        self.safe_print("System ID:   %s/%s#%s" % (self.user.id, self.user.name, self.user.discriminator))
        

        print("Note: This log file contains the servers TenshiBot is on, invoked commands and errors for debugging purposes")

        owner = self._get_owner(voice=True) or self._get_owner()
        if owner and self.servers:
            self.safe_print("Owner: %s/%s#%s\n" % (owner.id, owner.name, owner.discriminator))

            print('Server List:')
            [self.safe_print(' - ' + s.name + ' / ' + s.id) for s in self.servers]

        elif self.servers:
            print("Owner could not be found on any server (id: %s)\n" % self.config.owner_id)

            print('Server List:')
            [self.safe_print(' - ' + s.name + '/' + s.id) for s in self.servers]

        else:
            print("Owner unknown, bot is not on any servers.")
            if self.user.bot:
                print("\nTo make the bot join a server, paste this link in your browser.")
                print("Note: You should be logged into your main account and have \n"
                      "manage server permissions on the server you want the bot to join.\n")
                print("    " + await self.generate_invite_link())

        print()

        print("Server Count: " + str(len(self.servers)))

        if self.config.bound_channels:
            chlist = set(self.get_channel(i) for i in self.config.bound_channels if i)
            chlist.discard(None)
            invalids = set()

            invalids.update(c for c in chlist if c.type == discord.ChannelType.voice)
            chlist.difference_update(invalids)
            self.config.bound_channels.difference_update(invalids)

            print("Bound to text channels:")
            [self.safe_print(' - %s/%s' % (ch.server.name.strip(), ch.name.strip())) for ch in chlist if ch]

            if invalids and self.config.debug_mode:
                print("\nNot binding to voice channels:")
                [self.safe_print(' - %s/%s' % (ch.server.name.strip(), ch.name.strip())) for ch in invalids if ch]

            print()

        else:
            print("")




    async def cmd_helpold(self, channel, author, command=None):
        """
            view all commands        
        """

        if command:
            cmd = getattr(self, 'cmd_' + command, None)
            if cmd:
                return Response(
                    "```\n{}```".format(
                        dedent(cmd.__doc__),
                        command_prefix=self.config.command_prefix
                    ),
                    delete_after=60
                )
            else:
                return Response("No help available for this command", delete_after=10)

        else:
            helpmsg = "All commands\n```"
            commands = []

            for att in dir(self):
                if att.startswith('cmd_') and att != 'cmd_help':
                    command_name = att.replace('cmd_', '').lower()
                    commands.append("{}{}".format(self.config.command_prefix, command_name))

            helpmsg += "\n".join(commands)
            helpmsg += "```"
            helpmsg += "To see what a command does run =help <command>\n"
            helpmsg += "**TenshiBot by Harry99710**\nFor information about new features and chat with other users join the official server: https://discord.gg/vAbzRG9"

        await self.safe_send_message(author, helpmsg)
        await self.safe_send_message(channel, ":white_check_mark: Sent, check PMs")

    async def cmd_cleanup(self, message, channel, server, author, search_range=50):
        """
        Deletes sent messages to clean up the the chat
        """

        try:
            float(search_range)  # lazy check
            search_range = min(int(search_range), 1000)
        except:
            return Response("Invalid number", reply=True, delete_after=8)

        await self.safe_delete_message(message, quiet=True)

        def is_possible_command_invoke(entry):
            valid_call = any(
                entry.content.startswith(prefix) for prefix in [self.config.command_prefix])  # can be expanded
            return valid_call and not entry.content[1:2].isspace()

        delete_invokes = True
        delete_all = channel.permissions_for(author).manage_messages or self.config.owner_id == author.id

        def check(message):
            if is_possible_command_invoke(message) and delete_invokes:
                return delete_all or message.author == author
            return message.author == self.user

        if self.user.bot:
            if channel.permissions_for(server.me).manage_messages:
                deleted = await self.purge_from(channel, check=check, limit=search_range, before=message)
                return Response('Cleaned up {} message{}.'.format(len(deleted), 's' * bool(deleted)), delete_after=15)

        deleted = 0
        async for entry in self.logs_from(channel, search_range, before=message):
            if entry == self.server_specific_data[channel.server]['last_np_msg']:
                continue

            if entry.author == self.user:
                await self.safe_delete_message(entry)
                deleted += 1
                await asyncio.sleep(0.21)

            if is_possible_command_invoke(entry) and delete_invokes:
                if delete_all or entry.author == author:
                    try:
                        await self.delete_message(entry)
                        await asyncio.sleep(0.21)
                        deleted += 1

                    except discord.Forbidden:
                        delete_invokes = False
                    except discord.HTTPException:
                        pass

        return Response('Cleaned up {} message{}.'.format(deleted, 's' * bool(deleted)), delete_after=15)

    async def cmd_scleanup(self, message, channel, server, author, search_range=50):
        """
        Deletes sent messages to clean up the the chat
        """

        try:
            float(search_range)  # lazy check
            search_range = min(int(search_range), 1000)
        except:
            return Response("Invalid number", reply=True, delete_after=8)

        await self.safe_delete_message(message, quiet=True)

        def is_possible_command_invoke(entry):
            valid_call = any(
                entry.content.startswith(prefix) for prefix in [self.config.command_prefix])  # can be expanded
            return valid_call and not entry.content[1:2].isspace()

        delete_invokes = True
        delete_all = channel.permissions_for(author).manage_messages or self.config.owner_id == author.id

        def check(message):
            if is_possible_command_invoke(message) and delete_invokes:
                return delete_all or message.author == author
            return message.author == self.user

        if self.user.bot:
            if channel.permissions_for(server.me).manage_messages:
                deleted = await self.purge_from(channel, check=check, limit=search_range, before=message)
#                return Response('Cleaned up {} message{}.'.format(len(deleted), 's' * bool(deleted)), delete_after=15)

        deleted = 0
        async for entry in self.logs_from(channel, search_range, before=message):
            if entry == self.server_specific_data[channel.server]['last_np_msg']:
                continue

            if entry.author == self.user:
                await self.safe_delete_message(entry)
                deleted += 1
                await asyncio.sleep(0.21)

            if is_possible_command_invoke(entry) and delete_invokes:
                if delete_all or entry.author == author:
                    try:
                        await self.delete_message(entry)
                        await asyncio.sleep(0.21)
                        deleted += 1

                    except discord.Forbidden:
                        delete_invokes = False
                    except discord.HTTPException:
                        pass

#        return Response('Cleaned up {} message{}.'.format(deleted, 's' * bool(deleted)), delete_after=15)





    @owner_only
    async def cmd_setname(self, leftover_args, name):
        """
        Usage:
            {command_prefix}setname name

        Changes the bot's username.
        Note: This operation is limited by discord to twice per hour.
        """

        name = ' '.join([name, *leftover_args])

        try:
            await self.edit_profile(username=name)
        except Exception as e:
            raise exceptions.CommandError(e, expire_in=20)

        return Response(":ok_hand:", delete_after=20)

    @owner_only
    async def cmd_setnick(self, server, channel, leftover_args, nick):
        """
        Change TenshiBot's nickname
        """

        if not channel.permissions_for(server.me).change_nickname:
            raise exceptions.CommandError("Unable to change nickname: no permission.")

        nick = ' '.join([nick, *leftover_args])

        try:
            await self.change_nickname(server.me, nick)
        except Exception as e:
            raise exceptions.CommandError(e, expire_in=20)

#        return Response("", delete_after=20)

        await self.safe_send_message(channel, "set to `" + message.content[len("=setnick"):].strip() + "`")

    @owner_only
    async def cmd_setavatar(self, message, url=None):
        """
        Change TenshiBot's avatar (owner only command)
        """

        if message.attachments:
            thing = message.attachments[0]['url']
        else:
            thing = url.strip('<>')

        try:
            with aiohttp.Timeout(10):
                async with self.aiosession.get(thing) as res:
                    await self.edit_profile(avatar=await res.read())

        except Exception as e:
            raise exceptions.CommandError("Unable to change avatar: %s" % e, expire_in=20)

        return Response(":warning: avatar updated", delete_after=20)
        return Response(":warning: Update <https://discordbots.org/bot/252442396879486976> to reflect the avatar change!", delete_after=20)





    @owner_only
    async def cmd_reboot(self, channel):
        """
        Reboot TenshiBot (owner only command)
        """
        await self.safe_send_message(channel, ":timer: Please wait warmly...")
#        await self.disconnect_all_voice_clients()
        raise exceptions.RestartSignal

    @owner_only
    async def cmd_advreboot(self, channel):
        """
        Spawns a new process and kills this one (owner only command)
        """
        await self.safe_send_message(channel, ":warning: advanced reboot")
        os.system("/root/tenshilauncher.sh")
        raise exceptions.TerminateSignal
    
    @owner_only
    async def cmd_shutdown(self, channel):
        """
        Ends TenshiBot's process without rebooting the VPS (owner only command)
        """
        await self.safe_send_message(channel, ":warning: Shut down")
        raise exceptions.TerminateSignal

    async def on_message(self, message):
        await self.wait_until_ready()

        message_content = message.content.strip()
        if not message_content.startswith(self.config.command_prefix):
#            if not message_content.startswith("tenshi "):
#                if not message_content.startswith("tb!"):
                    return

#        message_content = message.content.strip()
#        if not message_content.startswith("tb!"):
#            return

        if message.author == self.user:
            self.safe_print("Ignoring command from myself (%s)" % message.content)
            return

        if message.author.bot:
            self.safe_print("Ignoring command from another bot (%s)" % message.content)
            await self.safe_send_message(message.channel, ":information_source: Commands can only be used by humans")
            return

        if self.config.bound_channels and message.channel.id not in self.config.bound_channels and not message.channel.is_private:
            return  # if I want to log this I just move it under the prefix check

        command, *args = message_content.split()  # Uh, doesn't this break prefixes with spaces in them (it doesn't, config parser already breaks them)
        command = command[len(self.config.command_prefix):].lower().strip()
#        command = command[len("tb!"):].lower().strip()

        handler = getattr(self, 'cmd_%s' % command, None)
        if not handler:
            return

        if message.channel.is_private:
            return



#maindisplay

        else:
            self.safe_print("[Command] {0.id}/{0.name}/{0.server} ({1})".format(message.author, message_content, self.servers, message.channel))

        user_permissions = self.permissions.for_user(message.author)

        argspec = inspect.signature(handler)
        params = argspec.parameters.copy()

        # noinspection PyBroadException
        try:
            if user_permissions.ignore_non_voice and command in user_permissions.ignore_non_voice:
                await self._check_ignore_non_voice(message)

#            if not (message.author.id == self.config.owner_id and command == 'console'):
#                await self.send_message(message.channel, 'You cannot use this bot in private messages.')

            handler_kwargs = {}
            if params.pop('message', None):
                handler_kwargs['message'] = message

            if params.pop('channel', None):
                handler_kwargs['channel'] = message.channel

            if params.pop('author', None):
                handler_kwargs['author'] = message.author

            if params.pop('server', None):
                handler_kwargs['server'] = message.server

            if params.pop('player', None):
                handler_kwargs['player'] = await self.get_player(message.channel)

            if params.pop('permissions', None):
                handler_kwargs['permissions'] = user_permissions

            if params.pop('user_mentions', None):
                handler_kwargs['user_mentions'] = list(map(message.server.get_member, message.raw_mentions))

            if params.pop('channel_mentions', None):
                handler_kwargs['channel_mentions'] = list(map(message.server.get_channel, message.raw_channel_mentions))

            if params.pop('voice_channel', None):
                handler_kwargs['voice_channel'] = message.server.me.voice_channel

            if params.pop('leftover_args', None):
                handler_kwargs['leftover_args'] = args

            args_expected = []
            for key, param in list(params.items()):
                doc_key = '[%s=%s]' % (key, param.default) if param.default is not inspect.Parameter.empty else key
                args_expected.append(doc_key)

                if not args and param.default is not inspect.Parameter.empty:
                    params.pop(key)
                    continue

                if args:
                    arg_value = args.pop(0)
                    handler_kwargs[key] = arg_value
                    params.pop(key)

            if message.author.id != self.config.owner_id:
                if user_permissions.command_whitelist and command not in user_permissions.command_whitelist:
                    raise exceptions.PermissionsError(
                        "This command is not enabled for your group (%s)." % user_permissions.name,
                        expire_in=20)

                elif user_permissions.command_blacklist and command in user_permissions.command_blacklist:
                    raise exceptions.PermissionsError(
                        "This command has been disabled for your group (%s)." % user_permissions.name,
                        expire_in=20)

            if params:
                docs = getattr(handler, '__doc__', None)
                if not docs:
                    docs = 'Usage: {}{} {}'.format(
                        self.config.command_prefix,
#                        "tb!",
                        command,
                        ' '.join(args_expected)
                    )

                docs = '\n'.join(l.strip() for l in docs.split('\n'))
                await self.safe_send_message(
                    message.channel,
                    '```\n%s\n```' % docs.format(command_prefix=self.config.command_prefix),
#                    expire_in=60
                )
                return

            response = await handler(**handler_kwargs)
            if response and isinstance(response, Response):
                content = response.content
                if response.reply:
                    content = '%s, %s' % (message.author.mention, content)

                sentmsg = await self.safe_send_message(
                    message.channel, content,
                    expire_in=response.delete_after if self.config.delete_messages else 0,
                    also_delete=message if self.config.delete_invoking else None
                )

        except (exceptions.CommandError, exceptions.HelpfulError, exceptions.ExtractionError) as e:
            print("{0.__class__}: {0.message}".format(e))

            expirein = e.expire_in if self.config.delete_messages else None
            alsodelete = message if self.config.delete_invoking else None

            await self.safe_send_message(
                message.channel,
                '```\n%s\n```' % e.message,
                expire_in=expirein,
                also_delete=alsodelete
            )

        except exceptions.Signal:
            raise

        except Exception:
            traceback.print_exc()
            if self.config.debug_mode:
                await self.safe_send_message(message.channel, ":warning: A system error has occured")



    async def on_server_join(self, server):
            self.safe_print("[Info] New server get! - {} ".format(server))

    async def on_server_remove(self, server):
            self.safe_print("[Info] Kicked from a server - {} ".format(server))

#            await self.reconnect_voice_client(after)

    async def cmd_aboutold(self, channel, message):
        """
        Version, Uptime and Server count
        """
        second = time.time() - st
        minute, second = divmod(second, 60)
        hour, minute = divmod(minute, 60)
        day, hour = divmod(hour, 24)
        week, day = divmod(day, 7)
        await self.safe_send_message(channel, "TenshiBot version 1.1r4, Created by Harry99710\n" + "currently on `" + str(len(self.servers)) + "` servers" + "\n" )
        return Response("System Uptime = %d weeks," % (week) + " %d days," % (day) + " %d hours," % (hour) + " %d minutes," % (minute) + " and %d seconds." % (second), delete_after=0)

    async def cmd_about(self, channel):

        second = time.time() - st
        minute, second = divmod(second, 60)
        hour, minute = divmod(minute, 60)
        day, hour = divmod(hour, 24)
        week, day = divmod(day, 7)

        em = discord.Embed(title='Currently on ' + str(len(self.servers)) + ' servers', description='Uptime= %d weeks,' % (week) + ' %d days,' % (day) + ' %d hours,' % (hour) + ' %d minutes,' % (minute) + ' and %d seconds.' % (second) + '\n Created by 99710', colour=0x00ffff)
        em.set_author(name='TenshiBot V1.1.4', icon_url=self.user.avatar_url)
        await self.send_message(channel, embed=em)

    async def cmd_uptime(self, channel, message):
        return Response("System Uptime = %d weeks," % (week) + " %d days," % (day) + " %d hours," % (hour) + " %d minutes," % (minute) + " and %d seconds." % (second), delete_after=0)



    async def cmd_rate(self, something, channel):
        """
        rate <something>
        """
        await self.safe_send_message(channel, "I rate it " + str(randint(0,10)) + "/10")

    async def cmd_techno2139849324234(self, channel):
        """
        Techno.bat, I wonder what this file does...
        """
        await self.safe_send_message(channel, "***TECHNO TECHNO TECHNO***")
        await asyncio.sleep(0.9)
        await self.safe_send_message(channel, "*** TECHNO TECHNO TECHNO***")
        await asyncio.sleep(0.9)
        await self.safe_send_message(channel, "***  TECHNO TECHNO TECHNO***")
        await asyncio.sleep(0.9)
        await self.safe_send_message(channel, ">Don't touch the keyboard<")
        await asyncio.sleep(0.9)
        await self.safe_send_message(channel, "***   TECHNO TECHNO TECHNO***")
        await asyncio.sleep(0.9)
        await self.safe_send_message(channel, "***    TECHNO TECHNO TECHNO***")
        await asyncio.sleep(0.9)
        await self.safe_send_message(channel, "***     TECHNO TECHNO TECHNO***")
        await asyncio.sleep(0.9)
        await self.send_file(channel, "pics/techno.png")

    @owner_only
    async def cmd_vpsreboot(self, channel):
        """
        Reboots the VPS (owner only command)
        """
        await self.safe_send_message(channel, "Rebooting the VPS..." )
        os.system("mv /root/Desktop/TenshiBot/log.txt /root/Desktop/TenshiBot/prevlog.txt")
        os.system("reboot")
        time.sleep(0.7)
        await self.safe_send_message(channel, "**Error:** Not running from crontab, run ~vpsreboot on Rtel or manually reboot the VPS via SSH/VNC" )

    async def cmd_latency(self, channel):
#        await self.safe_send_message(channel, "System OK! \nNow running ping test")
#        time.sleep(1.2)
        pingtime = time.time()
        pingms = await self.send_message(channel, ":timer:")
        ping = time.time() - pingtime
        await self.edit_message(pingms, "Latency =`%.03f Seconds`" % (ping))

    async def cmd_editmsg(self, channel, message):
        await self.edit_message(message, message.content[len("=editmsg "):].strip())

    async def cmd_siddump(self, server, author, leftover_args, cat='all'):
        """
         Silent list id's
        """
#        await self.safe_delete_message(message, quiet=True)
        cats = ['channels', 'roles', 'users']

        if cat not in cats and cat != 'all':
            return Response(
                "Valid categories: " + ' '.join(['`%s`' % c for c in cats]),
                reply=True,
                delete_after=25
            )

        if cat == 'all':
            requested_cats = cats
        else:
            requested_cats = [cat] + [c.strip(',') for c in leftover_args]

        data = ['Your ID: %s' % author.id]

        for cur_cat in requested_cats:
            rawudata = None

            if cur_cat == 'users':
                data.append("\nUser IDs:")
                rawudata = ['%s #%s: %s' % (m.name, m.discriminator, m.id) for m in server.members]

            elif cur_cat == 'roles':
                data.append("\nRole IDs:")
                rawudata = ['%s: %s' % (r.name, r.id) for r in server.roles]

            elif cur_cat == 'channels':
                data.append("\nText Channel IDs:")
                tchans = [c for c in server.channels if c.type == discord.ChannelType.text]
                rawudata = ['%s: %s' % (c.name, c.id) for c in tchans]

                rawudata.append("\nVoice Channel IDs:")
                vchans = [c for c in server.channels if c.type == discord.ChannelType.voice]
                rawudata.extend('%s: %s' % (c.name, c.id) for c in vchans)

            if rawudata:
                data.extend(rawudata)

        with BytesIO() as sdata:
            sdata.writelines(d.encode('utf8') + b'\n' for d in data)
            sdata.seek(0)

            # TODO: Fix naming (Discord20API-ids.txt)
            await self.send_file(author, sdata, filename='%s-ids-%s.txt' % (server.name.replace(' ', '_'), cat))
        
    async def cmd_confused(self, channel):
        """
        Dude what?
        """
        await self.send_file(channel, "pics/confused.jpg")

    async def cmd_magic(self, channel):
        """
        It's magic!
        """
        await self.send_file(channel, "pics/magic.png")

       
    async def cmd_shitpost(self, channel, message):
       return Response(random.choice(shitpost), delete_after=0)
            
    async def cmd_honk2(self):
        return Response(random.choice(honkhonk), delete_after=0)

    async def cmd_eurobeat(self):
        return Response(random.choice(eurobeat), delete_after=0)

    async def cmd_meme(self, channel, message):
        await self.send_file(channel, "pics/memes/" + random.choice(os.listdir("pics/memes")))

#oj_img

    async def cmd_oj(self, channel, message):
        await self.send_file(channel, "pics/oj/" + random.choice(os.listdir("pics/oj")))

    async def cmd_saki(self, channel, message):
        await self.send_file(channel, "pics/saki/" + random.choice(os.listdir("pics/saki")))

    async def cmd_suguri(self, channel, message):
        await self.send_file(channel, "pics/suguri/" + random.choice(os.listdir("pics/suguri")))

    async def cmd_nath(self, channel, message):
        await self.send_file(channel, "pics/nath/" + random.choice(os.listdir("pics/nath")))

    async def cmd_starbreaker(self, channel, message):
        await self.send_file(channel, "pics/starbreak/" + random.choice(os.listdir("pics/starbreak")))

    async def cmd_kae(self, channel, message):
        await self.send_file(channel, "pics/kae/" + random.choice(os.listdir("pics/kae")))

    async def cmd_kyoko(self, channel, message):
        await self.send_file(channel, "pics/kyoko/" + random.choice(os.listdir("pics/kyoko")))

    async def cmd_sherry(self, channel, message):
        await self.send_file(channel, "pics/sherry/" + random.choice(os.listdir("pics/sherry")))

#th_img

    async def cmd_honk(self, channel, message):
        await self.send_file(channel, "pics/touhou/honk/" + random.choice(os.listdir("pics/touhou/honk")))

    async def cmd_rinnosuke(self, channel, message):
        await self.send_file(channel, "pics/touhou/rinnosuke/" + random.choice(os.listdir("pics/touhou/rinnosuke")))

    async def cmd_murasa(self, channel, message):
        await self.send_file(channel, "pics/touhou/murasa/" + random.choice(os.listdir("pics/touhou/murasa")))

    async def cmd_mamizou(self, channel, message):
        await self.send_file(channel, "pics/touhou/mamizou/" + random.choice(os.listdir("pics/touhou/mamizou")))

    async def cmd_shou(self, channel, message):
        await self.send_file(channel, "pics/touhou/shou/" + random.choice(os.listdir("pics/touhou/shou")))

    async def cmd_nemuno(self, channel, message):
        await self.send_file(channel, "pics/touhou/nemuno/" + random.choice(os.listdir("pics/touhou/nemuno")))

    async def cmd_eternity(self, channel, message):
        await self.send_file(channel, "pics/touhou/eternity/" + random.choice(os.listdir("pics/touhou/eternity")))

    async def cmd_narumi(self, channel, message):
        await self.send_file(channel, "pics/touhou/narumi/" + random.choice(os.listdir("pics/touhou/narumi")))

    async def cmd_daiyousei(self, channel, message):
        await self.send_file(channel, "pics/touhou/daiyousei/" + random.choice(os.listdir("pics/touhou/daiyousei")))

    async def cmd_ringo(self, channel, message):
        await self.send_file(channel, "pics/touhou/ringo/" + random.choice(os.listdir("pics/touhou/ringo")))

    async def cmd_kosuzu(self, channel, message):
        await self.send_file(channel, "pics/touhou/kosuzu/" + random.choice(os.listdir("pics/touhou/kosuzu")))

    async def cmd_akyuu(self, channel, message):
        await self.send_file(channel, "pics/touhou/akyuu/" + random.choice(os.listdir("pics/touhou/akyuu")))

    async def cmd_hatate(self, channel, message):
        await self.send_file(channel, "pics/touhou/hatate/" + random.choice(os.listdir("pics/touhou/hatate")))

    async def cmd_mima(self, channel, message):
        await self.send_file(channel, "pics/touhou/mima/" + random.choice(os.listdir("pics/touhou/mima")))

    async def cmd_lily(self, channel, message):
        await self.send_file(channel, "pics/touhou/lily/" + random.choice(os.listdir("pics/touhou/lily")))

    async def cmd_shion(self, channel, message):
        await self.send_file(channel, "pics/touhou/shion/" + random.choice(os.listdir("pics/touhou/shion")))

    async def cmd_joon(self, channel, message):
        await self.send_file(channel, "pics/touhou/joon/" + random.choice(os.listdir("pics/touhou/joon")))

    async def cmd_seiran(self, channel, message):
        await self.send_file(channel, "pics/touhou/seiran/" + random.choice(os.listdir("pics/touhou/seiran")))

    async def cmd_koakuma(self, channel, message):
        await self.send_file(channel, "pics/touhou/koakuma/" + random.choice(os.listdir("pics/touhou/koakuma")))

    async def cmd_raiko(self, channel, message):
        await self.send_file(channel, "pics/touhou/raiko/" + random.choice(os.listdir("pics/touhou/raiko")))

    async def cmd_yukkuri(self, channel, message):
        await self.send_file(channel, "pics/touhou/yukkuri/" + random.choice(os.listdir("pics/touhou/yukkuri")))

    async def cmd_okina(self, channel, message):
        await self.send_file(channel, "pics/touhou/okina/" + random.choice(os.listdir("pics/touhou/okina")))

    async def cmd_mai(self, channel, message):
        await self.send_file(channel, "pics/touhou/mai/" + random.choice(os.listdir("pics/touhou/mai")))

    async def cmd_satono(self, channel, message):
        await self.send_file(channel, "pics/touhou/satono/" + random.choice(os.listdir("pics/touhou/satono")))

    async def cmd_aunn(self, channel, message):
        await self.send_file(channel, "pics/touhou/aunn/" + random.choice(os.listdir("pics/touhou/aunn")))

    async def cmd_komachi(self, channel, message):
        await self.send_file(channel, "pics/touhou/komachi/" + random.choice(os.listdir("pics/touhou/komachi")))

    async def cmd_wakasagihime(self, channel, message):
        await self.send_file(channel, "pics/touhou/wakasagihime/" + random.choice(os.listdir("pics/touhou/wakasagihime")))

    async def cmd_seija(self, channel, message):
        await self.send_file(channel, "pics/touhou/seija/" + random.choice(os.listdir("pics/touhou/seija")))

    async def cmd_rei(self, channel, message):
        await self.send_file(channel, "pics/touhou/rei/" + random.choice(os.listdir("pics/touhou/rei")))

    async def cmd_toyohime(self, channel, message):
        await self.send_file(channel, "pics/touhou/toyohime/" + random.choice(os.listdir("pics/touhou/toyohime")))

    async def cmd_yorihime(self, channel, message):
        await self.send_file(channel, "pics/touhou/yorihime/" + random.choice(os.listdir("pics/touhou/yorihime")))

    async def cmd_renko(self, channel, message):
        await self.send_file(channel, "pics/touhou/renko/" + random.choice(os.listdir("pics/touhou/renko")))

    async def cmd_maribel(self, channel, message):
        await self.send_file(channel, "pics/touhou/maribel/" + random.choice(os.listdir("pics/touhou/maribel")))

    async def cmd_nue(self, channel, message):
        await self.send_file(channel, "pics/touhou/nue/" + random.choice(os.listdir("pics/touhou/nue")))

    async def cmd_iku(self, channel, message):
        await self.send_file(channel, "pics/touhou/iku/" + random.choice(os.listdir("pics/touhou/iku")))

    async def cmd_elly(self, channel, message):
        await self.send_file(channel, "pics/touhou/elly/" + random.choice(os.listdir("pics/touhou/elly")))

    async def cmd_kasen(self, channel, message):
        await self.send_file(channel, "pics/touhou/kasen/" + random.choice(os.listdir("pics/touhou/kasen")))

    async def cmd_keine(self, channel, message):
        await self.send_file(channel, "pics/touhou/keine/" + random.choice(os.listdir("pics/touhou/keine")))

    async def cmd_konngara(self, channel, message):
        await self.send_file(channel, "pics/touhou/konngara/" + random.choice(os.listdir("pics/touhou/konngara")))

    async def cmd_meiling(self, channel, message):
        await self.send_file(channel, "pics/touhou/meiling/" + random.choice(os.listdir("pics/touhou/meiling")))

    async def cmd_yuyuko(self, channel, message):
        await self.send_file(channel, "pics/touhou/yuyuko/" + random.choice(os.listdir("pics/touhou/yuyuko")))

    async def cmd_flandre(self, channel, message):
        await self.send_file(channel, "pics/touhou/flandre/" + random.choice(os.listdir("pics/touhou/flandre")))

    async def cmd_aya(self, channel, message):
        await self.send_file(channel, "pics/touhou/aya/" + random.choice(os.listdir("pics/touhou/aya")))

    async def cmd_cirno(client, channel, message):
        #await self.send_file(channel, "pics/touhou/cirno/" + random.choice(os.listdir("pics/touhou/cirno")))
        #await self.safe_send_message(channel, "Cirno images are being refreshed, please wait warmly...")
        #await self.safe_send_message(channel, "also happy Cirno day from the bot dev")


#local fallback, inase sbooru doesn't work
        if message.content == "=cirno local":
            await client.send_file(channel, "pics/touhou/cirno/" + random.choice(os.listdir("pics/touhou/cirno")))    
        else:

#Pull images from sbooru instead of local, using char tag so this command can be used with other characters easily
            char = 'Cirno'

#solo tag to deal with any manga images
            r = requests.get('http://safebooru.org/index.php?page=dapi&s=post&q=index&tags=solo+' + char)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "lxml")
                num = int(soup.find('posts')['count'])
                maxpage = int(round(num/100))
                page = random.randint(0, maxpage)
                t = soup.find('posts')
                p = t.find_all('post')
                if num == 0:
                    msg = 'No posts found'
                else:
                    if num < 100:
                        pic = p[random.randint(0,num-1)]
                    elif page == maxpage:
                        pic = p[random.randint(0,num%100 - 1)]
                    else:
                        pic = p[random.randint(0,99)]
                    msg = pic['file_url']
                    #default is no source
                    #source = 'no source given'
                    #if len(pic['source']) != 0:
                        #source = pic['source']

#pretty sure i'm doing something wrong if i'm having to append the http part manually but eh... improvise, adapt, overcome 
                await client.send_message(message.channel, 'http:' + msg)
                #await client.send_message(message.channel, source)
            else:
                msg = 'An error has occured'
                await client.send_message(message.channel, msg)

    async def cmd_nitori(self, channel, message):
        await self.send_file(channel, "pics/touhou/nitori/" + random.choice(os.listdir("pics/touhou/nitori")))

    async def cmd_sumireko(self, channel, message):
        await self.send_file(channel, "pics/touhou/sumireko/" + random.choice(os.listdir("pics/touhou/sumireko")))

    async def cmd_okuu(self, channel, message):
        await self.send_file(channel, "pics/touhou/okuu/" + random.choice(os.listdir("pics/touhou/okuu")))

    async def cmd_patchy(self, channel, message):
        await self.send_file(channel, "pics/touhou/patchy/" + random.choice(os.listdir("pics/touhou/patchy")))

    async def cmd_rumia(self, channel):
        await self.send_file(channel, "pics/touhou/rumia/" + random.choice(os.listdir("pics/touhou/rumia")))

    async def cmd_youmu(self, channel):
        await self.send_file(channel, "pics/touhou/youmu/" + random.choice(os.listdir("pics/touhou/youmu")))

    async def cmd_tenshi(self, channel):
        await self.send_file(channel, "pics/touhou/tenshi/" + random.choice(os.listdir("pics/touhou/tenshi")))

    async def cmd_koishi(self, channel):
        await self.send_file(channel, "pics/touhou/koishi/" + random.choice(os.listdir("pics/touhou/koishi")))

    async def cmd_mokou(self, channel):
        await self.send_file(channel, "pics/touhou/mokou/" + random.choice(os.listdir("pics/touhou/mokou")))

    async def cmd_moko(self, channel):
        await self.send_file(channel, "pics/touhou/moko/" + random.choice(os.listdir("pics/touhou/moko")))

    async def cmd_reimu(self, channel):
        await self.send_file(channel, "pics/touhou/reimu/" + random.choice(os.listdir("pics/touhou/reimu")))

    async def cmd_satori(self, channel):
        await self.send_file(channel, "pics/touhou/satori/" + random.choice(os.listdir("pics/touhou/satori")))

    async def cmd_pc98(self, channel):
        await self.send_file(channel, "pics/touhou/pc98/" + random.choice(os.listdir("pics/touhou/pc98")))

    async def cmd_sakuya(self, channel):
        await self.send_file(channel, "pics/touhou/sakuya/" + random.choice(os.listdir("pics/touhou/sakuya")))

    async def cmd_wan(self, channel):
        await self.send_file(channel, "pics/touhou/momiji/" + random.choice(os.listdir("pics/touhou/momiji")))

    async def cmd_ran(self, channel):
        await self.send_file(channel, "pics/touhou/ran/" + random.choice(os.listdir("pics/touhou/ran")))

    async def cmd_kagerou(self, channel):
        await self.send_file(channel, "pics/touhou/kagerou/" + random.choice(os.listdir("pics/touhou/kagerou")))

    async def cmd_marisa(self, channel):
        await self.send_file(channel, "pics/touhou/marisa/" + random.choice(os.listdir("pics/touhou/marisa")))

    async def cmd_reisen(self, channel):
        await self.send_file(channel, "pics/touhou/reisen/" + random.choice(os.listdir("pics/touhou/reisen")))

    async def cmd_letty(self, channel):
        await self.send_file(channel, "pics/touhou/letty/" + random.choice(os.listdir("pics/touhou/letty")))

    async def cmd_remilia(self, channel):
        await self.send_file(channel, "pics/touhou/remilia/" + random.choice(os.listdir("pics/touhou/remilia")))

    async def cmd_suwako(self, channel):
        await self.send_file(channel, "pics/touhou/suwako/" + random.choice(os.listdir("pics/touhou/suwako")))

    async def cmd_shizuha(self, channel):
        await self.send_file(channel, "pics/touhou/shizuha/" + random.choice(os.listdir("pics/touhou/shizuha")))

    async def cmd_sanae(self, channel):
        await self.send_file(channel, "pics/touhou/sanae/" + random.choice(os.listdir("pics/touhou/sanae")))

    async def cmd_clownpiece(self, channel):
        await self.send_file(channel, "pics/touhou/clownpiece/" + random.choice(os.listdir("pics/touhou/clownpiece")))

    async def cmd_yukari(self, channel):
        await self.send_file(channel, "pics/touhou/yukari/" + random.choice(os.listdir("pics/touhou/yukari")))

    async def cmd_yuuka(self, channel):
        await self.send_file(channel, "pics/touhou/yuuka/" + random.choice(os.listdir("pics/touhou/yuuka")))

    async def cmd_suika(self, channel):
        await self.send_file(channel, "pics/touhou/suika/" + random.choice(os.listdir("pics/touhou/suika")))

    async def cmd_sekibanki(self, channel):
        await self.send_file(channel, "pics/touhou/sekibanki/" + random.choice(os.listdir("pics/touhou/sekibanki")))

    async def cmd_wriggle(self, channel):
        await self.send_file(channel, "pics/touhou/wriggle/" + random.choice(os.listdir("pics/touhou/wriggle")))

    async def cmd_hina(self, channel):
        await self.send_file(channel, "pics/touhou/hina/" + random.choice(os.listdir("pics/touhou/hina")))

    async def cmd_alice(self, channel):
        await self.send_file(channel, "pics/touhou/alice/" + random.choice(os.listdir("pics/touhou/alice")))

    async def cmd_kyouko(self, channel):
        await self.send_file(channel, "pics/touhou/kyouko/" + random.choice(os.listdir("pics/touhou/kyouko")))

    async def cmd_kisume(self, channel):
        await self.send_file(channel, "pics/touhou/kisume/" + random.choice(os.listdir("pics/touhou/kisume")))

    async def cmd_nazrin(self, channel):
        await self.send_file(channel, "pics/touhou/nazrin/" + random.choice(os.listdir("pics/touhou/nazrin")))

    async def cmd_sukuna(self, channel):
        await self.send_file(channel, "pics/touhou/sukuna/" + random.choice(os.listdir("pics/touhou/sukuna")))

    async def cmd_kokoro(self, channel):
        await self.send_file(channel, "pics/touhou/kokoro/" + random.choice(os.listdir("pics/touhou/kokoro")))

    async def cmd_yoshika(self, channel):
        await self.send_file(channel, "pics/touhou/yoshika/" + random.choice(os.listdir("pics/touhou/yoshika")))

    async def cmd_seiga(self, channel):
        await self.send_file(channel, "pics/touhou/seiga/" + random.choice(os.listdir("pics/touhou/seiga")))

    async def cmd_kogasa(self, channel):
        await self.send_file(channel, "pics/touhou/kogasa/" + random.choice(os.listdir("pics/touhou/kogasa")))

    async def cmd_futo(self, channel):
        await self.send_file(channel, "pics/touhou/futo/" + random.choice(os.listdir("pics/touhou/futo")))

    async def cmd_miko(self, channel):
        await self.send_file(channel, "pics/touhou/miko/" + random.choice(os.listdir("pics/touhou/miko")))

    async def cmd_mystia(self, channel):
        await self.send_file(channel, "pics/touhou/mystia/" + random.choice(os.listdir("pics/touhou/mystia")))

    async def cmd_genjii(self, channel):
        await self.send_file(channel, "pics/touhou/genjii/" + random.choice(os.listdir("pics/touhou/genjii")))

    async def cmd_byakuren(self, channel):
        await self.send_file(channel, "pics/touhou/byakuren/" + random.choice(os.listdir("pics/touhou/byakuren")))

    async def cmd_hecatia(self, channel):
        await self.send_file(channel, "pics/touhou/hecatia/" + random.choice(os.listdir("pics/touhou/hecatia")))

    async def cmd_junko(self, channel):
        await self.send_file(channel, "pics/touhou/junko/" + random.choice(os.listdir("pics/touhou/junko")))

    async def cmd_sagume(self, channel):
        await self.send_file(channel, "pics/touhou/sagume/" + random.choice(os.listdir("pics/touhou/sagume")))

    async def cmd_doremy(self, channel):
        await self.send_file(channel, "pics/touhou/doremy/" + random.choice(os.listdir("pics/touhou/doremy")))

    async def cmd_minoriko(self, channel):
        await self.send_file(channel, "pics/touhou/minoriko/" + random.choice(os.listdir("pics/touhou/minoriko")))

    async def cmd_yamame(self, channel):
        await self.send_file(channel, "pics/touhou/yamame/" + random.choice(os.listdir("pics/touhou/yamame")))

    async def cmd_yuugi(self, channel):
        await self.send_file(channel, "pics/touhou/yuugi/" + random.choice(os.listdir("pics/touhou/yuugi")))

    async def cmd_parsee(self, channel):
        await self.send_file(channel, "pics/touhou/parsee/" + random.choice(os.listdir("pics/touhou/parsee")))

    async def cmd_tewi(self, channel):
        await self.send_file(channel, "pics/touhou/tewi/" + random.choice(os.listdir("pics/touhou/tewi")))

    async def cmd_medicine(self, channel):
        await self.send_file(channel, "pics/touhou/medicine/" + random.choice(os.listdir("pics/touhou/medicine")))

    async def cmd_prismriver(self, channel):
        await self.send_file(channel, "pics/touhou/prismriver/" + random.choice(os.listdir("pics/touhou/prismriver")))

    async def cmd_eiki(self, channel):
        await self.send_file(channel, "pics/touhou/eiki/" + random.choice(os.listdir("pics/touhou/eiki")))

    async def cmd_orin(self, channel):
        await self.send_file(channel, "pics/touhou/orin/" + random.choice(os.listdir("pics/touhou/orin")))

    async def cmd_kaguya(self, channel):
        await self.send_file(channel, "pics/touhou/kaguya/" + random.choice(os.listdir("pics/touhou/kaguya")))

    async def cmd_eirin(self, channel):
        await self.send_file(channel, "pics/touhou/erin/" + random.choice(os.listdir("pics/touhou/erin")))

    async def cmd_kanako(self, channel):
        await self.send_file(channel, "pics/touhou/kanako/" + random.choice(os.listdir("pics/touhou/kanako")))

    async def cmd_chen(self, channel):
        await self.send_file(channel, "pics/touhou/chen/" + random.choice(os.listdir("pics/touhou/chen")))

    async def cmd_star(self, channel):
        await self.send_file(channel, "pics/touhou/star/" + random.choice(os.listdir("pics/touhou/star")))

    async def cmd_luna(self, channel):
        await self.send_file(channel, "pics/touhou/luna/" + random.choice(os.listdir("pics/touhou/luna")))

    async def cmd_sunny(self, channel):
        await self.send_file(channel, "pics/touhou/sunny/" + random.choice(os.listdir("pics/touhou/sunny")))

    async def cmd_touhou(self, channel):
        await self.send_file(channel, "pics/touhou/" + random.choice(os.listdir("pics/touhou")))

#e_egg

    async def cmd_leisuresonorusdream(self, channel, message):
#        await self.safe_send_message(channel, "*?*")
        await self.send_file(channel, "pics/mountain.png")

    async def cmd_limbosilentdream(self, channel, message):
        await self.safe_send_message(channel, "*?*")

    async def cmd_logicsymbolicdream(self, channel, message):
        await self.safe_send_message(channel, "*?*")

#Re-enabled this, it's obsolete by the about command anyway...		
    @owner_only
    async def cmd_servercount(self):
        return Response(self.servers(), delete_after=0)

    @owner_only
    async def cmd_setstatus(self, channel, message):
        """
        Change TenshiBot's playing status (owner only command)
        """
        await self.change_presence(game=discord.Game(name=message.content[len("~setstatus"):].strip()))
        await self.safe_send_message(channel, "set to `" + message.content[len("~setstatus"):].strip() + "`")
    
    async def cmd_wangan(self, channel):
        """
        Display a random wangan midnight image
        """
        return await self.send_file(channel, random.choice(wangan))


    async def cmd_banana(self, channel, user, message):
        """
        Banana <name>
        """        
        await self.send_file(channel, "pics/banana.png")
        await self.safe_send_message(message.channel, "*" + message.content[len("~banana "):].strip() + "* has been BANAE NAED")

    async def cmd_atk2(self, channel, user, message):
        """
        Banana <name>
        """        
        await self.send_file(channel, "pics/banana.png")
        await self.safe_send_message(message.channel, "*" + message.content[len("~banana "):].strip() + "* has been BANAE NAED")

    async def cmd_jojo(self, channel, user, message):
        """
        Jojo <name>
        """

        
        await self.send_file(channel, "pics/stop.jpg")
        await self.safe_send_message(message.channel, "*" + message.content[len("~stop "):].strip() + "* has been STOPPED!")


#Cleverbot_io API, apparently this one is free. may still go off topic tho
    async def cmd_ai(client, message, question, channel):
        #this cleverbot engine has a delay so send a typing status to look like something is happening
        await client.send_typing(channel)
        unsplit = message.content.split("ai")
        split = unsplit[1]
        answer = (bot.ask(split))
        #await client.send_typing(channel)
        await client.send_message(message.channel, answer)


#    async def cmd_weather(client, message, location, channel):


#checking if the user specified gensokyo

#        if message.content == "=weather gensokyo":
#            return Response(random.choice(gensokyoweather), delete_after=0)
#        if message.content == "=weather enviromentcanada":
#            await client.send_file(channel, "pics/enviromentcanada.png")
#        else:
#            weather = Weather(unit=Unit.CELSIUS)
#        location = weather.lookup_by_location(message.content[len("=weather "):].strip())
#        condition = location.condition
#        await client.send_message(message.channel, "Current Conditions: " + condition.text +  "\n" + "Temperature: " + condition.temp + "C" )


    async def cmd_pepe(self, channel, message):
        """
        Feelsbadman
        """ 
        await self.send_file(channel, "pics/feelsbadman.png")

    async def cmd_bemani(self):
        """
        This is Konami's famous bemani series!
        """ 
        return Response(random.choice(koonami), delete_after=0)

    async def cmd_coinflip(self, channel, message):
        """
        Flip a coin
        """
        await self.safe_send_message(channel, "Flipping Coin..." )
        await asyncio.sleep(0.7) 
        return Response(random.choice(coinflip), delete_after=0)

    async def cmd_invite(self, channel, message):
        """
        Invite TenshiBot to your server
        """
        await self.safe_send_message(channel, "Use this link to add me to your server: <https://discordapp.com/oauth2/authorize?client_id=252442396879486976&scope=bot&permissions=67161152>" )

    async def cmd_hooray(self, channel, message):
        """
        Cirno Hooray!
        """
        await self.send_file(channel, "pics/hooray.png")

    async def cmd_redzone(self, channel, message):
        await self.safe_send_message(channel, "**SAY SPEED RAVE!!**")

    @owner_only
    async def cmd_logdump(self, channel, author):
        """
        Sends the log file located at /root/Desktop/TenshiBot/log.txt
        """
        await self.send_file(author, "log.txt")
        await self.safe_send_message(channel, "check pm")

    async def cmd_csay(self, channel, message):
        """
        Classic say, original say command if you perfer it over the standard say command
        """
        await self.safe_send_message(message.channel, message.author.name + ":mega:: " + message.content[len("=csay "):].strip())

    async def cmd_boop(self, channel, message):
        await self.safe_send_message(channel, "*boops back*")

#google images addon test command gitest

    async def cmd_gitest(self, channel, message):
        await self.safe_send_message(channel, "dev_gitest")

        response = google_images_download.googleimagesdownload("tenshi")
        absolute_image_paths = response.download()


    async def cmd_patreon(self, channel, message):
        await self.safe_send_message(channel, "Want to support TenshiBot on patreon? \n Patreon donators get a donator role and can request a custom colour in the TenshiBot Hangout Discord\nhttp://patreon.com/tenshibot")

    async def cmd_space_test(self, channel, message):
        await self.safe_send_message(channel, "working")

    async def cmd_blech(self, channel, message):
        await self.safe_send_message(channel, "<:cirBlech:325342918330155008>")

    async def cmd_naisumeme(self, channel, message):
        await self.safe_send_message(channel, "Indeed")

    async def cmd_emojitest(self, channel, message):
        await self.safe_send_message(channel, "<:sr94:230222135291936769>")

    async def cmd_dsay(self, channel, message):
        """
        Delete say, a say command that deletes the invoking message. usage is same as standard say command
        """
        await self.safe_delete_message(message, quiet=True)
        await self.safe_send_message(message.channel, message.content[len("=dsay "):].strip())

    async def cmd_react(self, channel, message):
        """
        Delete say, a say command that deletes the invoking message. usage is same as standard say command
        """
        await self.add_reaction(message, message.content[len("=react "):].strip())

    @owner_only		
    async def cmd_pin2(self, channel, message):
        """
        Delete say, a say command that deletes the invoking message. usage is same as standard say command
        """
        await self.pin_message(message)

    async def cmd_emote(self, channel, message):
        """
        emote from another server
        """
        await self.safe_send_message(message.channel, "<" + message.content[len("=emoji "):].strip() + ">")

    async def cmd_semote(self, channel, message):
        """
        emote from another server
        """
        await self.safe_delete_message(message, quiet=True)
        await self.safe_send_message(message.channel, "<" + message.content[len("=semote "):].strip() + ">")



    async def cmd_md(self, channel, message):
        """
        get the id of something
        """
        await self.safe_send_message(message.channel, "`" + message.content[len("=md"):].strip() + "`")

#dev_?
#(idk what this was, i think i was testing something with RTEL)

    @owner_only		
    async def cmd_sensay(self, channel, message):
        """
        Delete say, a say command that deletes the invoking message. usage is same as standard say command
        """
        await self.safe_delete_message(message, quiet=True)
        await self.safe_send_message(message.channel, message.content[len("=sensay "):].strip())
        s = await self.safe_send_message(channel, "hc68cl 1")
        await asyncio.sleep(0.5)
        await self.safe_delete_message(s, quiet=True)

    async def cmd_say(self, channel, message):
        """
        Say <text>
        """
        await self.safe_send_message(message.channel, message.content[len("=say "):].strip())

    async def cmd_support(self, channel, message):
        """
        Support server link
        """
        await self.safe_send_message(channel, "Need help with something or just want to chat with other users? Join TenshiBot Hangout: https://discord.gg/vAbzRG9")

        
    async def cmd_thonk(self, channel, message):
        """
        Hm....
        """
        await self.send_file(channel, "pics/thonk.gif")

    async def cmd_oil(self, channel, user, message):
        """
        oil <name>
        """
        await self.send_file(channel, "pics/oil.png")
        await self.safe_send_message(message.channel, "*" + message.content[len("~oil "):].strip() + "* has been OILED!")

    async def cmd_roll(self):
        return Response(random.choice(dice), delete_after=0)

    async def cmd_8ball(self, channel, question, message):
        return Response(random.choice(fortune), delete_after=0)
        """
        8ball <question>
        """

    async def cmd_doubleroll(self):
        return Response(random.choice(doubledice), delete_after=0)

    async def cmd_commandlist(self, channel, author, command=None):
        """
            view all commands        
        """
        cmds = open("commands/standard.txt", "r")
        commands = cmds.read()
        await self.safe_send_message(author, commands)
        await self.safe_send_message(channel, ":white_check_mark: Sent, check PMs")

    async def cmd_emotelist(self, channel, author, command=None):
        """
        List of emoji for the =emote command       
        """
        emote = open("commands/emote.txt", "r")
        commands = emote.read()
        await self.safe_send_message(author, commands)
        await self.safe_send_message(channel, ":white_check_mark: Sent, check PMs")

#dev_console
        
    @owner_only
    async def cmd_console(self, channel, command, message):
        """
        =console <command>
        (owner only command)      
        """
        os.system(message.content[len("=console"):].strip())
        await self.safe_send_message(channel, ":warning: Command run, check the log for any errors")

#dev_silent_nickname_set		
		
    @owner_only
    async def cmd_ssetnick(self, server, channel, message, leftover_args, nick):
        """
        Change TenshiBot's nickname
        """

        if not channel.permissions_for(server.me).change_nickname:
            raise exceptions.CommandError(":warning: Failed to change nickname, invalid permission")

        nick = ' '.join([nick, *leftover_args])

        try:
            await self.change_nickname(server.me, nick)
        except Exception as e:
            raise exceptions.CommandError(e, expire_in=20)
        await self.safe_delete_message(message, quiet=True)

#dev_send_file
		
    @owner_only
    async def cmd_sendfile(self, channel, file, message):
        """
        =sendfile <file path>
        Send a file from the VPS (owner only)

        Useful stuff:
        Tenshibot directory - /root/Desktop/TenshiBot/
        VPS Logfiles - /var/log/
        """
        await self.send_file(channel, message.content[len("~sendfile "):].strip())

    @owner_only
    async def cmd_leaveserver(self, id, channel):
        """
            =leaveserver <id>
        Make tenshibot leave a server
        """
        target = self.get_server(id)
        if target is None:
            await self.safe_send_message(channel, ":warning: Can't leave a server i'm not on...")
        else:
            await self.safe_send_message(channel, "Now leaving...")
            await self.leave_server(target)
            return Response("rip {0.name}  (ID: {0.id})".format(target))

#dev_remote nickname set

    @owner_only
    async def cmd_rsetnick(self, id, channel, message):
        """
            =leaveserver <id>
        Make tenshibot leave a server
        """
        target = self.get_server(id)
        if target is None:
            await self.safe_send_message(channel, ":warning: Can't leave a server i'm not on...")
        else:
            await self.safe_send_message(channel, "Now leaving...")
            await self.change_nickname(target, "test")
            return Response("rip {0.name}  (ID: {0.id})".format(target))

#dev_invite_gen

    @owner_only
    async def cmd_inv2(self, id, channel, author):
        """
            =inv2 <id>
        Get an invite to a server (owner only command)
        """
        target = self.get_server(id)
        if target is None:
            await self.safe_send_message(channel, ":warning: not on that server...")
        else:
            inv = await self.create_invite(target)
            await self.safe_send_message(channel, inv)
            await self.safe_send_message(channel, ">> {0.name}  (ID: {0.id}) <<".format(target))

#dev_msg_pin_by_id

    @owner_only
    async def cmd_pin(self, id, channel, author):
        """
            =pin <id>
        Pin a message (owner only command)
        """
        target = self.get_message(id)
        if target is None:
            await self.safe_send_message(channel, ":warning: Invalid ID")
        else:
            inv = await self.pin_message(target)
#            await self.safe_send_message(channel, inv)
#            await self.safe_send_message(channel, ">> {0.name}  (ID: {0.id}) <<".format(target))

#dev_ban_test

    @owner_only
    async def cmd_tenshiban(self, id, channel, author):
        """
            =leaveserver <id>
        Make tenshibot leave a server
        """
        target = server.member(id)
        if target is None:
            await self.safe_send_message(channel, ":warning: Can't leave a server i'm not on...")
        else:
            inv = await self.ban(target)

#dev_kick_test
			
    @owner_only
    async def cmd_tenshikick(self, id, channel, author):
        """
            =leaveserver <id>
        Make tenshibot leave a server
        """
        target = server.member(id)
        if target is None:
            await self.safe_send_message(channel, "Invalid member")
        else:
            inv = await self.kick(target)

#WORKING!!
    async def cmd_iftest(self, arg, channel, message):
        """
        """
#        if message.content[len("=iftest"):].strip() == "Tenshi":
        if message.content == "=iftest T":
            await self.safe_send_message(channel, "Neko Miko Reimu")
        else:
            await self.safe_send_message(channel, "Neko Miko sanae")

#dev_kick_test_2

    @owner_only
    async def cmd_hammer(self, server, member, channel, message):
        """
            =leaveserver <id>
        Make tenshibot leave a server
        """
#        target = "id"
#        if target is None:
#            await self.safe_send_message(channel, ":warning: Can't leave a server i'm not on...")
#        else:
        await self.kick(member.id)
#            await self.safe_send_message(author, inv)
        return Response(">> {0.name}  (ID: {0.id}) <<".format(target))



#help_cmd
    async def cmd_help(self, author, message, channel, command=None):

        if message.content == "=help html":

            await self.safe_send_message(channel, "View my commands here http://193.70.38.209/tb_command.html")
            return


        else:

            cmds = open("commands/sectionlist.txt", "r")
        commands = cmds.read()

        if command:
            cmd = getattr(self, 'cmd_' + command, None)
            if cmd:
                return Response(
                    "```\n{}```".format(
                        dedent(cmd.__doc__),
                        command_prefix=self.config.command_prefix
                    ),
                    delete_after=60
                )
            else:
                return Response("No help available for this command", delete_after=10)

        else:
            await self.safe_send_message(author, commands)
            await self.safe_send_message(channel, ":white_check_mark: Sent, check PMs")

#help_commands			
			
# --help sections--
#1: Touhou
#2: General
#3: Fun
#4: System
#5: Debugging

    async def cmd_help1(self, author, message, channel, command=None):
        cmds = open("commands/toho.txt", "r")
        commands = cmds.read()
        await self.safe_send_message(author, commands)
        await self.safe_send_message(channel, ":white_check_mark: Sent, check PMs")

    async def cmd_help2(self, author, message, channel, command=None):
        cmds = open("commands/general.txt", "r")
        commands = cmds.read()
        await self.safe_send_message(author, commands)
        await self.safe_send_message(channel, ":white_check_mark: Sent, check PMs")

    async def cmd_help3(self, author, message, channel, command=None):
        cmds = open("commands/fun.txt", "r")
        commands = cmds.read()
        await self.safe_send_message(author, commands)
        await self.safe_send_message(channel, ":white_check_mark: Sent, check PMs")

    async def cmd_help4(self, author, message, channel):
        cmds = open("commands/system.txt", "r")
        commands = cmds.read()
        await self.safe_send_message(author, commands)
        await self.safe_send_message(channel, ":white_check_mark: Sent, check PMs")

    async def cmd_help5(self, author, message, channel):
        cmds = open("commands/debug2.txt", "r")
        commands = cmds.read()
        await self.safe_send_message(author, commands)
        await self.safe_send_message(channel, ":eyes:")

    async def cmd_tbcredits(self, author, message, channel, command=None):
        cmds = open("commands/credits.txt", "r")
        commands = cmds.read()
        await self.safe_send_message(author, commands)
        await self.safe_send_message(channel, ":white_check_mark: Sent, check PMs")


    async def cmd_embedtest(self, channel, message):

        em = discord.Embed(title='Neko Miko Reimu', description='Neko Miko Reimu', colour=0xDEADBF)
        em.set_author(name='embed', icon_url="http://hakurei.co.uk/neko.png")
        await self.send_message(channel, embed=em)

#Net neturality awareness command		
    async def cmd_neturalnet(self, channel, message):

        em = discord.Embed(title='TenshiBot has been blocked by your ISP', description='visit https://battleforthenet.com to prevent this', colour=0xDEADBF)
        em.set_author(name='Error!', icon_url=self.user.avatar_url)
        await self.send_message(channel, embed=em)

#dev_remote_say
    @owner_only
    async def cmd_rsay(self, channel, message):
        await self.send_message(discord.Object(id=369389053017194497), message.content[len("=rsay "):].strip())

#dev_gbooru_test
#First steps to getting sbooru working, leave this as owner only as gbooru can return R-18 stuff
    @owner_only
    async def cmd_gboorutest(client, author, message, channel):
        if len(message.content.split()) == 1:
            r = requests.get('http://gelbooru.com/index.php?page=post&s=random').url
            pid = getID(r)
            r2 = requests.get('http://gelbooru.com/index.php?page=dapi&s=post&q=index&id=' + str(pid))
            if r2.status_code == 200:
                soup = BeautifulSoup(r2.text, "lxml")
                pmsg = ((soup.find('post'))['file_url'])
                msg = pmsg.format(message)
                await client.send_message(message.channel, msg)
                #source = ((soup.find('post'))['source'])
                #await client.send_message(message.channel, source)
            else:
                msg = 'Unable to find tag'
                await client.send_message(message.channel, msg)


#dev_sbooru_search
    async def cmd_safebooru(client, author, message, channel):
            s = message.content.split()
            r = requests.get('http://safebooru.org/index.php?page=dapi&s=post&q=index&tags=' + s[1])
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "lxml")
                num = int(soup.find('posts')['count'])
                maxpage = int(round(num/100))

                #if there are less than 100 posts, stay on page 0
                page = random.randint(0, maxpage)

                #make the soup and get all posts
                t = soup.find('posts')
                p = t.find_all('post')

                #if there are no posts, something is wrong
                if num == 0:
                    msg = 'No posts found, are the tags spelt correctly?'
                else:
                    # only one page cus <100 results
                    if num < 100:
                        pic = p[random.randint(0,num-1)]
                    # if last page assuming >1 page, max element is last
                    elif page == maxpage:
                        pic = p[random.randint(0,num%100 - 1)]
                    else:
                        pic = p[random.randint(0,99)]
                    msg = pic['file_url']
                    #default is no source
                    #source = 'no source given'
                    #if len(pic['source']) != 0:
                        #source = pic['source']
                await client.send_message(message.channel, msg)
                #await client.send_message(message.channel, source)
            else:
                msg = 'An error has occured'
                await client.send_message(message.channel, msg)



#japanese commands, May not display correctly here on the VPS...


#japanese mokou command
    async def cmd_モコウ(self, channel):
        """
        藤原 妹紅

        """
        return await self.send_file(channel, random.choice(mokou))

#japanese help command (commandlist)
    async def cmd_コマンドリスト(self, author, channel, command=None):
        """
        ボットコマンドを表示する       
        """

        if command:
            cmd = getattr(self, channel, author, command=None)
            if cmd:
                return Response(
                    "```\n{}```".format(
                        dedent(cmd.__doc__),
                        command_prefix=self.config.command_prefix
                    ),
                    delete_after=60
                )
            else:
                return Response("利用不可", delete_after=10)

        else:
            helpmsg = "ボットコマンド\n```"
            commands = []

            for att in dir(self):
                if att.startswith('cmd_') and att != 'cmd_help':
                    command_name = att.replace('cmd_', '').lower()
                    commands.append("{}{}".format(self.config.command_prefix, command_name))

            helpmsg += "\n".join(commands)
            helpmsg += "```"
            helpmsg += "警告：日本語のサポートはベータです\n"
            helpmsg += "**Harry99710によって作成**\n公式サーバー https://discord.gg/vAbzRG9"

        await self.safe_send_message(author, helpmsg)
        await self.safe_send_message(channel, ":white_check_mark: あなたにメッセージを送った（* ^ω^）")


        
if __name__ == '__main__':
    bot = MusicBot()
    bot.run()
