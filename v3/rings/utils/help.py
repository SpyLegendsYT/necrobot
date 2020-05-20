from discord.ext import commands as cmd

class NecrobotHelp(cmd.HelpCommand):       
    def command_not_found(self, string):
        return f":negative_squared_cross_mark: | Command **{string}** not found."
        
    def subcommand_not_found(self, command, string):
        return f":negative_squared_cross_mark: | Command **{command.qualified_name}** has no sucommand **{string}**"
        
    def get_command_signature(self, command):
        """Retrieves the signature portion of the help page."""
        prefix = self.clean_prefix
        signature = command.signature.replace("<", "[").replace(">", "]")
        return f"{prefix}{command.qualified_name} {signature}"
        
    def get_ending_note(self):
        command_name = self.context.invoked_with
        return "\nCommands in `codeblocks` are commands you can use, commands with ~~strikethrough~~ you cannot use but you can still check the help. Commands in *italics* are recent additions.\n" \
               "Type {0}{1} [command] for more info on a command.(Example: `{0}help edain`)\n" \
               "You can also type {0}{1} [category] for more info on a category. Don't forget the first letter is always uppercase. (Example: `{0}help Animals`) \n".format(self.clean_prefix, command_name)
       
    async def format_command_name(self, command):
        async def predicate():
            try:
                return await command.can_run(self.context)
            except cmd.CommandError:
                return False

        valid = await predicate()
        if valid and command.enabled:
            if command.qualified_name in self.context.bot.new_commands:
                return f"***{command.qualified_name}***"
            
            return f"`{command.qualified_name}`"
        
        return f"~~{command.qualified_name}~~"
        
    async def get_brief_signature(self, command):
        first_line = command.help.split("\n")[0]
        formatted = first_line.format(usage=self.get_command_signature(command))[:100]
        
        return formatted
     
    async def send_bot_help(self, mapping):
        help_msg = f":information_source: **NecroBot Help Menu** :information_source:\n{self.context.bot.description}\n\n"

        for cog, commands in mapping.items():
            if not commands or cog is None:
                continue
            
            if cog.qualified_name == 'Support':
                commands.extend(mapping[None])
            
            cog_msg = f"**{cog.qualified_name}** - "
            command_list = []
            for command in commands:
                command_list.append(await self.format_command_name(command))
                    
            help_msg += f"{cog_msg}{' | '.join(command_list)}\n"
            
        help_msg += self.get_ending_note()
        await self.get_destination().send(help_msg)
        
    async def send_cog_help(self, cog):
        help_msg = f":information_source: **{cog.qualified_name} Help Menu** :information_source:\n{cog.description}\n\n__Commands__\n"
        
        for command in cog.get_commands():
            name = await self.format_command_name(command)
            help_msg += f"`{name}`- {await self.get_brief_signature(command)}\n"
            
        help_msg += self.get_ending_note()
        await self.get_destination().send(help_msg)
        
    async def send_command_help(self, command):
        help_msg = f":information_source: **`{command}` command** :information_source:\n{command.help}"
        signature = f"__Usage__\n{self.get_command_signature(command)}"
        help_msg = help_msg.format(usage=signature, pre=self.clean_prefix)
        
        await self.get_destination().send(help_msg)
        
    async def send_group_help(self, group):
        help_msg = f":information_source: **`{group}` command** :information_source:\n{group.help}"
        signature = f"__Usage__\n{self.get_command_signature(group)}\n\n"
        help_msg = help_msg.format(usage=signature, pre=self.clean_prefix)
        
        for command in group.commands:
            name = await self.format_command_name(command)
            help_msg += f"`{name}`- {await self.get_brief_signature(command)}\n"
        
        await self.get_destination().send(help_msg)
