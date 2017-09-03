#!/usr/bin/python3.6
import discord
from discord.ext.commands import *
import itertools, inspect, re

class MissingAttrHandler(str):
    def __init__(self, format):
        self.format = format

    def __getattr__(self, attr):
        return type(self)('{}.{}'.format(self.format, attr))

    def __repr__(self):
        return MissingAttrHandler(self.format + '!r}')

    def __str__(self):
        return MissingAttrHandler(self.format + '!s}')

    def __format__(self, format):
        if self.format.endswith('}'):
            self.format = self.format[:-1]
        return '{}{}}}'.format(self.format, format)


class SafeDict(dict):
    def __missing__(self, key):
        return MissingAttrHandler('{{{}'.format(key))

class NecroBotHelpFormatter(HelpFormatter):
    def __init__(self, show_hidden=False, show_check_failure=True, width=80):
        self.width = width
        self.show_hidden = show_hidden
        self.show_check_failure = show_check_failure

    def filter_command_list(self):
        """Returns a filtered list of commands based on the two attributes
        provided, :attr:`show_check_failure` and :attr:`show_hidden`. Also
        filters based on if :meth:`is_cog` is valid.

        Returns
        --------
        iterable
            An iterable with the filter being applied. The resulting value is
            a (key, value) tuple of the command name and the command itself.
        """
        def predicate(tuple):
            cmd = tuple[1]
            if self.is_cog():
                # filter commands that don't exist to this cog.
                if cmd.instance is not self.command:
                    return False

            if cmd.hidden and not self.show_hidden:
                return False

            if self.show_check_failure:
                # we don't wanna bother doing the checks if the user does not
                # care about them, so just return true.
                return True

            try:
                return cmd.can_run(self.context) and self.context.bot.can_run(self.context)
            except CommandError:
                return False

        iterator = self.command.commands.items() if not self.is_cog() else self.context.bot.commands.items()
        return filter(predicate, iterator)

    def get_ending_note(self):
        command_name = self.context.invoked_with
        return "Commands in `codeblocks` are commands you can use, commands with ~~strikethrough~~ you cannot use but you can still check the help. \n" \
               "Type {0}{1} [command] for more info on a command.(Example: `{0}help edain`\n" \
               "You can also type {0}{1} [category] for more info on a category. Don't forget the first letter is always uppercase. (Example: `{0}help Animals`) \n".format(self.clean_prefix, command_name)

    def get_ending_note_command(self):
        command_name = self.context.invoked_with
        return "Type {0}{1} [command] [subcommand] for more info on a command's subcommand.\n" \
               "Example: `{0}help settings welcome-channel` - display help on the welcome-channel subcommand of the settings command \n".format(self.clean_prefix, command_name)

    def get_command_signature(self):
        """Retrieves the signature portion of the help page."""
        result = []
        prefix = self.clean_prefix
        cmd = self.command
        parent = cmd.full_parent_name
        if len(cmd.aliases) > 0:
            aliases = ' | '.join(cmd.aliases)
            fmt = '{0}[{1.name} | {2}]'
            if parent:
                fmt = '{0}{3} [{1.name} | {2}]'
            result.append(fmt.format(prefix, cmd, aliases, parent))
        else:
            name = prefix + cmd.name if not parent else prefix + parent + ' ' + cmd.name
            result.append(name)

        params = cmd.clean_params
        if len(params) > 0:
            for name, param in params.items():
                if param.kind == param.VAR_POSITIONAL:
                    result.append('[{}...]'.format(name))
                else:
                    result.append('<{}>'.format(name))

        return ' '.join(result)

    def _add_commands_to_page(self, max_width, commands):
        commandList = list()
        for name, command in commands:
            if name in command.aliases:
                # skip aliases
                continue

            if command.can_run(self.context) and self.context.bot.can_run(self.context):
                commandList.append("`{}`".format(name))
            else:
                commandList.append("~~{}~~".format(name))

        return " | ".join(commandList)

    def _add_subcommands_to_page(self, max_width, commands):
        for name, command in commands:
            if name in command.aliases:
                # skip aliases
                continue
            if command.can_run(self.context) and self.context.bot.can_run(self.context):
                entry = '  `{0:<{width}}` - {1}'.format(name, command.short_doc, width=max_width)
            else:
                entry = '  ~~{0:<{width}}~~ - {1}'.format(name, command.short_doc, width=max_width)

            shortened = self.shorten(entry)
            self._paginator.add_line(shortened)

    def format(self):
        self._paginator = Paginator(prefix="", suffix="")
        if isinstance(self.command, Command):
            title = ":information_source: **The `{0}` command** :information_source:".format(self.command)
        else:
            title = ":information_source: **NecroBot Help Menu** :information_source:"


        self._paginator.add_line(title)

        # we need a padding of ~80 or so

        description = self.command.description if not self.is_cog() else inspect.getdoc(self.command)

        if description:
            # <description> portion
            self._paginator.add_line(description, empty=True)

        if isinstance(self.command, Command):
            # <signature portion>
            signature = "__Usage__\n" + self.get_command_signature()

            # <long doc> section
            if self.command.help:
                line = self.command.help.format_map(SafeDict(usage=signature, pre=self.clean_prefix))
                self._paginator.add_line(line, empty=True)            

            # end it here if it's just a regular command
            if not self.has_subcommands():
                self._paginator.close_page()
                return self._paginator.pages

        max_width = self.max_name_size

        def category(tup):
            cog = tup[1].cog_name
            # we insert the zero width space there to give it approximate
            # last place sorting position.
            return "**" + cog + '** - ' if cog is not None else '\u200b**No Category** - '

        if self.is_bot():
            data = sorted(self.filter_command_list(), key=category)
            counter = 0
            for category, commands in itertools.groupby(data, key=category):
                # there simply is no prettier way of doing this.
                counter += 1
                commands = list(commands)
                if len(commands) > 0:
                    self._paginator.add_line(str(counter) + ". " + category +  self._add_commands_to_page(max_width, commands))

            # add the ending note for general help
            ending_note = self.get_ending_note()

        else:
            self._paginator.add_line('__Commands__')
            self._add_subcommands_to_page(max_width, self.filter_command_list())

            # add the ending note for command pages
            ending_note = self.get_ending_note_command()
           
        self._paginator.add_line(empty=True)
        self._paginator.add_line(ending_note)
        return self._paginator.pages
