#!/usr/bin/python3.6
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import random
from bs4 import BeautifulSoup
import aiohttp

class Social():
    """All of NecroBot's fun commands to keep a user active and entertained"""
    def __init__(self, bot):
        self.bot = bot
        #Tarot Cards
        self.tarot_list = ["**The Fool**: You are about to embark a new journey, some would say you're going on an adventure. There will be much peril but rewards too. Your innocence, spontaneity will get your free spirited self very far. ","**The Fool Reversed**: Something is about to happen, a new event is about to begin but I sense many hardships, be weary I sense evil near. Keep your recklessness, naivety and foolishness in check or all that risk taking could cost you dearly. ","**The Magician**: Knowledge will be an important part of the next few months of your life, stay focused on the task at hand and you might just make it. Power is near at hand but it will require concentration, resourcefulness, skill and pro-activity. Do not let the occasion slip through your fingers. ","**The Magician Reversed**: There is something odd about the upcoming events... something... unnatural. Be weary of the one that comes to you with sweet words for their true intentions may not be known. If you do not carefully plan what you are about to do it could be a lost opportunity doubled with betrayal of one close to you. ","**The High Priestess**: A thought has been nagging you at the back of your head and your intuition has been begging you to listen to it. And yet you still prefer to follow your own path. A bold choice for sure but one that could be made much easier if you did follow what the higher powers of the world tried to tell you. ","**The High Priestess Reversed**: Something is clouding your mind, you have not revealed your true intentions to your close ones. Be careful hidden agendas often lead to harm, best to listen to your inner voice and reveal your project. ","**The Empress**: Mother Nature smiles to you, the shape you have desired for a long time in within grasp, perhaps a rectxact with nature will give you the necessary arm length to reach what you have desired for so long. Happy news can be expected. ","**The Empress Reversed**: Now is not the time to isolate yourself. Your head is buzzing with ideas but you can't put them all down on paper on your own. It would be wasted potential to try and do this alone, best to rely on your friends and family, seek help if you feel as though the earth swallowing you up. ","**The Emperor**: Good news is on the way, your recent efforts have not gone unnoticed and a position of power will be offered to you. Now or never to make use of your intellect and experience in the matter, this is only the beginning of a new era, your era. Others will depend on you. ","**The Emperor Reversed**: Those belows you will test your patience this month, bringing new ideas that will almost seem heretical to you, resist the urge to burn them at the stake and open your mind. Total ctxrol and rigidity is not always the best answer, be flexible, understand why they demand such things. ","**The Hierophant**: You have learned much since your days as a student, and it is now your turn for you to teach others. Many seek entry to places you visit, guide them so that they may join you in the bliss you have gained. Let them find themselves through your teachings. ","**The Hierophant Reversed**: Your mind is full with ideas, and to you they seem like ones that will better this world. However, slow down and take a moment to think: is it really worth risking the status quo for them? The world is in a fragile balance, it would be best not to shatter it. Perhaps another time. ","**The Lovers**: A new day dawns on your relation, or the possibility of one, your are about to discover new things about your partner that will surprise you and bring you pleasure, many things that you once found boring will now be painted with a new coat of excitement. Don't be afraid to try new things, as they may be the key. ","**The Lovers Reversed**: Oh no, it's not looking too good. Question your relation, is it really meant for you? The initial fire of love that devoured you is beginning to fade and you start questioning your decisions. Do not let these doubts consume you, talk to your partner, they may feel the same. ","**The Chariot**: Your strength and determination have brought you new lands, whether physical or metaphysical. You desire to explore these lands and exert your ctxrol and them, after all why not? Victory is yours but be weary of foolish destruction. Balance is key to all. ","**The Chariot Reversed**: A loss of ctxrol can often lead to a disastrous crash, before moving on to new activities make sure you have a good grasp on your life. Sometimes it is best to slow down in order to arrive at your destination intact. ","**The World Reversed**: You are trying to achieve completion in your life but you may not be taking all the steps necessary to achieve your goals. There is a tendency to take the easiest or quickest path to attain your goal but often this does not lead to the outcome you had originally intended.","**The Strength**: The stars have looked down on you and found you worthy, great strength will be given to you this month. Try everything for you have a chance to achieve it, do not let what used to be drag you down for your new powers make anything possible. ","**The Strength Reversed**: Doubt fills your mind, do not let the great emptiness of the Void fill your heart, {username, for the world has grown full of peril and everywhere love is no mingled with grief. You feel weak this month, now is the time to think about your choices and decide what to do. The stars are not with you this month, fall back on what you know is possible. ","**The Hermit**: Your head is feeling heavy, this world's constant need for social interaction has left you empty and full of nonsense. Now is the time to take a break, to get away from everything. You have a strong need to understand, not just at the surface level but to really know why life is the way it is. ","**The Hermit Reversed**: You have been away from the world for too long, you are beginning to mistake the feeling of isolation for loneliness. You have withdrawn yourself from the world but you will soon need people, time to ctxact the world once more and come back to your loved ones. You will need them soon. ","**The Wheel of Fortune**: Luck is on your side, dare all. A change is in the air, your recent acts have not gone unnoticed, you will be rewarded. A cycle of hardship comes to an end and rewards are upon you. ","**The Wheel of Fortune Reversed**:Luck is not on your side. There has been a turn of events that are not in your favour sending you into a tail spin and changing your world significantly, seemingly for the worst. There are negative forces at play that are outside of your ctxrol, leaving you feeling helpless and powerless. ","**The Justice**: It is time for you to realize that your decisions and actions have long-term consequences and your present and future circumstances are most likely a result of these decisions and actions. You need to know and speak the truth and perceive it in the words and deeds of others. Be fair and just with all and you will soon be able to detect dishonesty in yourself and others. Learn the rules that govern what you are involved with. ","**The Justice Reversed**: You are not actively accepting responsibility for your actions and may be trying to dodge the bullet and blame others for your mistakes. The key here is to take responsibility for your own situation and realise that you are here through your own past choices. ","**The Hanged Man**: A need to suspend action, and as a result, a period of indecision is indicated. Decisions or actions that need to be implemented will be postponed, even if, at the time, there is a sense of urgency to act. You need an emotional release from whatever it is that is leaving you feeling stuck. ","**The Hanged Man Reversed**: You feel you are sacrificing a lot and getting nothing in return. You may have felt things were at an absolute standstill, with no movement or resolution. You may be putting off making a decision, in the hope that it will all sort itself out eventually. However, this is often just wishful thinking. ","**Death**: Death is symbolic of the ending of a major phase or aspect of your life that may bring about the beginning of something far more valuable and important. You must close one door in order to open another. You need to put the past behind you and part ways, to embrace new opportunities and possibilities. ","**Death Reversed**: You are on the verge of major change but for some reason, you are resisting that change. You are reluctant to let go of the past or you may not know how to make the change you need. You are carrying harmful aspects from the past that interfere with the opportunity you have for a new beginning. ","**Temperance**: You are beginning to learn to bring balance to your life. It may seem impossible but don't give up now. You may feel as though you are paddling messily underwater to keep a neat appearance but this is helping you. Soon it will feel natural and you will come out a better person. ","**Temperance Reversed**: something is out of balance, in conflict or excessive, and is therefore creating stress and tension in your life. Look to the other cards to understand what is out of balance. You are lacking long term vision and must understand how your actions now will affect the balance of your future life. What goes around comes around. ","**The Devil**: Hidden forces of negativity constrain you and are tricking you into thinking you are imprisoned by external forces ultimately out of your ctxrol. Now is the time for deep reflexions and thoughts on one's self. Understand who and what your are and rid yourself of the evil that has taken your heart. ","**The Devil Reversed**: Growing awareness that you are currently in this state and you desire freedom from these harmful bonds. You may now be more willing and able to accept changes in your life and you may be more open to taking on new perspectives. Do not give up now! ","**The Tower**: A great event is coming, something that will shake the foundations of your world. Do not fear, it is for the better, you will soon realize you were incomplete. Do not be afraid of the change that come after the storm, rather embrace it.","**The Tower Reversed**: You are simply delaying the necessary ‘destruction’. You need to go through this difficult time in order to learn an important lesson. Do not resist it. Even though it is shocking and hard to deal with, it is a very important part of your life journey. ","**The Star**:  Renewed hope and faith are upon you and a sense that you are truly blessed by the Universe. Courage, fulfillment, and inspiration are in your life. You are entering a loving phase in your life, filled with calm energy, mental stability and deeper understanding of both yourself and others around you. ","**The Star Reversed**: Your spiritual mission is distorted. Instead of hope, you are feeling despair or discouragement. Instead of being filled with positive possibilities, you find yourself dwelling on negative issues. Negative thoughts will wear away at you to the point where you may give up ctxrol of the situation and concede defeat.  ","**The Moon**: You are projecting fear into your present and your future, based on past experiences. The images, thoughts and feelings that you have repressed over time cause inner disturbances that are becoming overwhelming. As a result, you are now experiencing negative blocks within your personality, causing fear and anxiety. ","**The Moon Reversed**: A Fortuneundamental unhappiness with your present situation but also confusion over what else you could do and what you really want to do. It may be that you believe that what you really want to do with your life is impractical or unrealistic, or your past experiences in life have convinced you that you are stuck with what you have and it is too late to change now. ","**The Sun**: You have an innate sense of confidence right now. Life is good, the sun is shining and you are on your way to achieving your goals. You open the curtains with the sun shining on your face. Having struggled through the shadow sides you now know yourself and know where you are heading, and the sun illuminates your path. ","**The Sun Reversed**: Finding the positive aspects to a particular situation may prove to be difficult. The clouds may be blocking out the warmth, and preventing you from feeling as though everything is on track. You may have experienced setbacks that have damaged your enthusiasm and optimism and have perhaps led you to question whether you can really achieve what you have set out to achieve. ","**Judgment**: You have had a recent epiphany or an ‘awakening’ where you have come to a realisation that you need to live your life in a different way and you need to be true to yourself and your needs. You have opened yourself up to a new possibility – to lead a fulfilling life that serves your higher needs and that offers inspiration and hope to others. ","**Judgment Reversed**: You may be indulging yourself in doubt and self-judgement. Your deliberation is causing you to miss the new opportunities that await. A certain amount of momentum has accumulated behind what you have achieved, which could propel you further. ","**The World**: All of your efforts are finally paying off and you have reached the end of a journey or have completed a major life cycle. You have endured hardships and challenges along the way but these have only made you stronger and significantly wiser and more experienced than when you first started on your journey."]
        #LOTR Facts
        self.lotr_list = ["J.R.R. Tolkien, the author of Lord of the Rings didn’t invent the Elvish languages to fit into the Lord of the Rings timeline, but wrote Lord of the Rings as a background history for the 15 different languages he created. ","An Elvish language (Sindarin) J.R.R. Tolkien used for The Lord of the Rings was entirely independent from any other language, and as of 2008 ctxained some 25000 words. ","The budget for the two “The Hobbit” movies is almost twice the budget of the entire Lord of the Rings Trilogy. ","Tolkien considered Sam Gamgee the “chief hero” of The Lord of the Rings. ","In the original 1937 edition of “The Hobbit,” Gollum willingly bet his ring in a game of riddles with Bilbo and the two parted on good terms when the ring went ‘missing’. Tolkien changed the story in his second edition to reflect the corruptive powers of the ring taking shape in, “The Lord of the Rings” Trilogy. ","While filming Lord of the Rings in the mountainous New Zealand, Sean Bean refused a helicopter ride to a set that was high in the mountains due to his fear of flying. He instead hiked up to the set in his full Boromir armor every day that they shot up there. ","In 1999, a Russian author, Kirill Eskov published a novel that retold The Lord of The Rings from Sauron’s Perpective. In his version, he depicted Mordor as a peaceful country and Gandalf and Aragorn as evil. ","Surprisingly, Tolkien’s son, Christopher Tolkien hates The Lord of the Rings movies ","Christopher Lee (Saruman) was the only person involved with the Lord of the Rings films to have actually met Tolkien ","The Lord of the Rings novels were written as if they were translated to English, and the original common tongue of the books is called Westron. ","The Beatles once approached Stanley Kubrick with the idea of shooting Lord of the Rings movie that starred them. Kubrick told John Lennon, he felt the story was unfilmable.","The Beatles once approached Stanley Kubrick with the idea of shooting Lord of the Rings movie that starred them. Kubrick told John Lennon, he felt the story was unfilmable. ","Viggo Mortensen (Aragorn) bonded with the two horses that he rode in Lord of the Rings, so he purchased them from their owner. ","“The Lord of the Rings: The Return of the King” is the first and only fantasy film ever to win an Academy Award for “Best Picture”. ","Tolkien has often mentioned that War of the Rings takes place in the real world and that we are now currently in the Seventh Age. ","An International Astronomical Union regulation states that all mountains on Titan must be named after the mountains from The Lord of the Rings. ","According to Elijah Wood, he created his Lord of the Rings’ Frodo audition tape in the woods with a homemade Hobbit costume. ","While filming “The Lord of the Rings” trilogy, Viggo Mortensen got so into character that during a conversation, Peter Jackson referred to him as “Aragorn” for over half an hour without him even realizing it. ","JRR Tolkien’s estate only received $62,500 for the Lord of the Rings film trilogy until a lawsuit was filed. ","In The Lord of the Rings: The Return of the King’ (2003), they made a special effort to make sure that Sauron’s tower being destroyed did not resemble the World Trade Center attack. ","Gandalf’s famous quote “You shall not pass” line in the book/movie is an allusion to a propaganda slogan predating to World War 1 ","Around 10,000 prosthetic facial appliances, over 3,500 pairs of Hobbit feet, 2 500 foam body suits, 1,200 suits of armour, 2,000 weapons and 10,000 arrows were made for the Lord of The Rings trilogy.  ","Tolkien did not want the third Lord of the Rings book to be called ‘Return of the King’, as he felt it revealed too much about the story. This title was chosen by the publisher.  ","The gravestone of J.R.R. Tolkien and his wife is inscribed with “Lúthien” and “Beren”. They were two tragic legendary characters in The Lord of the Rings, who were madly in love. ","Housing at University of California, Irvine is called Middle Earth and each hall is named after a region or town in LOTR ","Sean Connery turned down the role of Gandalf in the Lord of the Rings trilogy, which cost him $300 million (he was offered 15% of the film’s profit). ","Frodo falls down exactly 39 times in The Lord of the Rings trilogy ","In the scene where Frodo is stabbed by Shelob’s stinger, Elijah Wood was actually stabbed with a prop one. ","It was Christopher Lee’s lifelong dream to play Gandalf in the LOTR movies. He auditioned for the role, but was given the part of Saruman instead because they thought he was too old to handle the fighting scenes.  ","The length of time from when Frodo first gets the ring to when he actually sets out on his adventure is 17 years, not a few weeks like the movie makes it seem. ","Cast members from ‘The Fellowship of the Ring‘, including Elijah Wood, Orlando Bloom and Viggo Mortensen, had the number nine in Elvish tattooed onto them after filming had ended. ","Ian McKellen kept some items from his time playing Gandalf, including the staff, sword and wizard’s hat. ","Sean Astin and Orlando Bloom were just two of the actors who sustained injuries while on set, and Viggo Mortensen broke two of his toes! ","Legolas is known for his white-blond hair in the films, but the books don’t actually specify his hair colour. ","‘The Return of the King‘ broke the record for the film with the highest amount of people featured in it. ","While Tolkien admitted that the books can be seen as being a reference to historical events, he did not intend them to be allegorical.","In the scene when Denethor attempts to burn Faramir on the pyre, the pyre could not truly be on fire because Gandalf's horse would not go near it. To solve this, the crew reflected a real fire onto a pane of glass in front of the camera so that it looks as though the pyre is burning. ","The dead oliphaunt carcass used in this film is reportedly the largest prop ever built for a motion picture. According to members of the prop department, director Peter Jackson still thought it could have been bigger. ","To get enough extras for the Battle at the Black Gate, a few hundred members of the New Zealand army were brought in. They apparently were so enthusiastic during the battle scenes that they kept breaking the wooden swords and spears they were given. ","Andy Serkis and Elijah Wood were each given prop rings by director Peter Jackson used in the movie. They both thought they had the only one. ","Great caution was taken for the scene where Faramir is dragged back to Minas Tirith on his horse. The filmmakers were afraid that the horse might suddenly start to run, dragging David Wenham behind it so a release system was built into the saddle. Wenham held a handle in his right hand, and if the horse started to run, he could simply pull it and be released from the stirrup. Fortunately, they ended up not needing it. ","Since John Rhys-Davies suffered constant rashes from wearing the Gimli make-up, the make-up department gave him the opportunity to throw his Gimli mask into the fire on his last day of pick-up photography. He didn't hesitate a moment to grab and burn it. ","Peter Jackson is arachnophobic and based the Shelob design on the types of spiders he feared the most.","Billy Boyd's singing scene largely came about because Philippa Boyens went for a night out at a karaoke bar with the younger male cast members and she was very struck by the quality of his voice. Remembering that Denethor asks Pippin to sing him a song when Faramir heads off to war, she resurrected the lyrics from the novel and Boyd himself came up with the tune for it. ","Viggo Mortensen estimates that during the course of filming the entire trilogy and including all takes, he 'killed' every stuntman on the production at least fifty times. ","According to a magazine article, Peter Jackson hated the Army of the Dead, thinking it was too unbelievable. He kept it in the script because he did not wish to disappoint diehard fans of the book trilogy. (Even though it wasn't the army of the Dead that liberated Minas Tirith in the book.) ","During one of the shots filming the charge of the Rohirrim, a horse rider fell off the back of his horse. All the horses that came behind him miraculously managed to either miss or avoid him. ","The first shot of Sam's arm coming into frame holding Sting towards Shelob is actually Peter Jackson's arm ","The battle scenes, which reportedly ctxain over 200,000 digital participants, are so huge that an extra room had to be built onto Weta Digital's effects facility to house all the computer equipment needed to render the scenes. ","Theoden touching the spears of his soldiers before they charge into battle was Bernard Hill's idea. ","Denethor (John Noble) carried a sword strapped to his belt. Although he never draws it, the prop department made a full sword that could be drawn from its sheath, so that Noble would feel as important as the rest of the cast which used their swords. ","Miranda Otto had to undergo numerous fittings to finally settle on a helmet that disguised her face yet revealed enough of it so that the audience would know who she was. ","The live-action Rohan army is made up of several hundred New Zealander extras, who responded to an open casting call for anyone who could ride a horse. Many of them were women, who had to perform male riders. The only woman in Rohirrim huge assault is obviously Eowyn. ","The oil that Denethor pours over himself and Faramir was a combination of water and glycerin, to achieve an appropriate glistening effect. Because this soaked the wigs and costumes, this scene had to be filmed in a single take. ","The scene where Aragorn's army assembles in front of the Black Gate of Mordor was shot in a desert that was used by the army as a training field. Because it was still littered with mines and bombs that hadn't gone off, the army had to sweep the field with metal detectors to make the danger for the actors and extras acceptable at least. ","For the lighting of the beacons sequence, one beacon was helicoptered up to the top of a mountain and then lit. The rest were all computer generated. ","Gollum says the word 'precious' seventeen times in this film. ","In the Extended Edition, the Mouth of Sauron is played by Australian actor Bruce Spence. Spence's real mouth was digitally enlarged to underscore his role in Sauron's service, as well as further give the character an inhuman aspect. ","The scene of the Rohirrim charging the Pelennor had to be filmed 52 times before the crew were satisfied with the take. During this process, about 60 of the 280 horses participating had to drop out for various reasons. ","Dominic Monaghan was allergic to the elven cloaks the Fellowship wore. Before scenes were shot, Peter Jackson used to joke around and say 'Are we ready to go? Does Dom have his cape on?'"]
        #Riddles
        self.riddles_list = [["What has roots as nobody sees,\nIs taller than trees,\nUp, up it goes,\nAnd yet never grows?", "mountain"], ["Thirty white horses on a red hill,\nFirst they champ,\nThen they stamp,\nThen they stand still.", "teeth"], ["Voiceless it cries,\nWingless flutters,\nToothless bites,\nMouthless mutters.", "wind"],["An eye in a blue face\nSaw an eye in a green face.\n'That eye is like to this eye'\nSaid the first eye,\n'But in low place,\nNot in high place.'","sun"],["It cannot be seen, cannot be felt,\nCannot be heard, cannot be smelt.\nIt lies behind stars and under hills,\nAnd empty holes it fills.\nIt comes first and follows after,\nEnds life, kills laughter.","dark"],["A box without hinges, key, or lid,\nYet golden treasure inside is hid.","egg"],["Alive without breath,\nAs cold as death;\nNever thirsty, ever drinking,\nAll in mail never clinking.","fish"],["This thing all things devours:\nBirds, beasts, trees, flowers;\nGnaws iron, bites steel;\nGrinds hard stones to meal;\nSlays king, ruins town,\nAnd beats high mountain down.","time"]]
        #Dad Jokes
        self.dad_joke = ["My ex-wife still misses me. But her aim is steadily improving.","If you spent your day in a well, can you say your day was well-spent?","Apparently taking a day off is not something you should do when you work for a calendar company.","If a wild pig kills you, does it mean you’ve been boared to death?","Jokes about unemployed people are not funny. They just don't work.","Which bees produce milk? The boo-bees!","I dig, you dig, she dig, we dig, you dig…the poem may not be beautiful, but it's certainly very deep.","You’re becoming a vegetarian? I think that’s a big missed steak.","I asked my dad for his best dad joke and he said, 'You.'","These puns are purr-fect...","A furniture store keeps calling me. But all I wanted was one night stand.","You heard the rumor going around about butter? Nevermind, I shouldn't spread it.","I wanted to tell you a joke about leeches. But I won’t – they all suck.","Do you know how Moses makes his tea? Hebrews it!","I wonder why there aren’t any more cemeteries around. People are really dying to get in there.","What do you call a fake noodle? An Impasta.","Want to hear a joke about paper? Nevermind it's tearable.","I'll call you later. Don't call me later, call me Dad.","What do you call an elephant that doesn't matter? An irrelephant","Want to hear a joke about construction? I'm still working on it.","Why couldn't the bicycle stand up by itself? It was two tired.","5/4 of people admit that they’re bad with fractions.","What do you call a fat psychic? A four-chin teller.","The rotation of earth really makes my day.","What's brown and sticky? A stick.","What kind of fish is made of only two sodium atoms? Two Na","What concert costs only 45 cents? 50 Cent ft. Nickelback","If a child refuses to take a nap, is he resisting a rest?","Want to hear a word I just made up? Plagiarism.","I gave all my dead batteries away today... Free of charge.","Nostalgia isn't what it used to be","Dad, did you get a haircut? No I got them all cut.","What do you call a Mexican who has lost his car? Carlos.","You know, people say they pick their nose, but I feel like I was just born with mine","I’m not indecisive. Unless you want me to be","The only thing worse than having diarrhea is having to spell it","I used to work in a shoe recycling shop. It was sole destroying.","What's the difference between in-laws and outlaws? Outlaws are wanted.","What's the leading cause of dry skin? Towels","I wear a stethoscope so that in a medical emergency I can teach people a valuable lesson about assumptions.","There are 10 types of people. Those who understand binary, and those who don't.","3.14% of sailors are pi-rates.","Archaeology really is a career in ruins...","I don't trust stairs. They're always up to something.","What do you get hanging off banana trees? Sore arms.","Found out I was colour blind the other day... That one came right out the purple.","When my wife told me to stop impersonating a flamingo I had to put my foot down.","What's the difference between a hippo and a zippo? One is really heavy, the other is a little lighter.","To the man in the wheelchair that stole my camouflage jacket... You can hide but you can't run.","Singing in the shower is all fun and games until you get shampoo in your mouth.... Then it's a soap opera","\"Does this uniform make me look fat\" - insecurity guard","You know what they say about cliffhangers...","I have the heart of a lion and a lifetime ban from London zoo.","https://pbs.twimg.com/media/B_0IAfEWYAAfzI8.jpg","A man said to me that he hadn't been to the toilet for 2 years. Reckon he's full of shit.","https://pbs.twimg.com/media/B64zuZpCYAA31hm.jpg","There's no way I'm in denial.","I got a reversible jacket for Christmas, I can't wait to see how it turns out.","Did you hear about the kidnapping at school? Its ok, he woke up.","Where are average things built? In the satisfactory."]


    @commands.command(aliases=["sean","joke"])
    @commands.cooldown(3, 5, BucketType.user)
    async def dadjoke(self, ctx):
        """Send a random dadjoke from a long list. Whoever PM's Necro with the reason for one of the aliases being "sean" gets a free 1,000 NecroBot currency.
        
        {usage}"""
        await ctx.channel.send(":speaking_head: | **{}**".format(random.choice(self.dad_joke)))

    @commands.command()
    @commands.cooldown(3, 5, BucketType.channel)
    async def riddle(self, ctx):
        """Ask a riddle to the user from a long list and waits 30 seconds for the answer. If the user fails to answer they go feed Gollum's fishies. To answer the riddle simply type out the answer, no need to prefix it with anything. 
        
        {usage}"""
        riddle = random.choice(self.riddles_list)
        await ctx.channel.send("Riddle me this {}: \n{}".format(ctx.message.author.name, riddle[0]))

        def check(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel

        msg = await self.bot.wait_for("message", check=check, timeout=30)

        if riddle[1] in msg.content.lower():
            await ctx.channel.send("Well played, that was the correct answer.")
        else:
            await ctx.channel.send("Wrong answer! Now you go to feed the fishies!")

    @commands.command()
    @commands.cooldown(3, 3, BucketType.user)
    async def tarot(self, ctx):
        """Using the mystical art of tarology, NecroBot reads the user's fate in the card and returns the explanation for each card. Not to be taken seriously. 
        
        {usage}"""
        card_list = random.sample(self.tarot_list, 3)
        await ctx.channel.send(":white_flower: | Settle down now and let Necro see your future my dear "+ ctx.message.author.name + "...\n**Card #1:** {}\n**Card #2:** {}\n**Card #3:** {}\n__*That is your fate, none can change it for better or worst.*__".format(card_list[0], card_list[1], card_list[2]))

    @commands.command()
    @commands.cooldown(3, 5, BucketType.user)
    async def rr(self, ctx, bullets : int = 1):
        """Plays a game of russian roulette with the user. If no number of bullets is entered it will default to one. 
        
        {usage}
        
        __Example__
        `{pre}rr 3` - game of russian roulette with 3 bullets
        `{pre}rr` - game of russian roulette with 1 bullet"""
        if bullets not in range(0,7):
            bullets = 1
            
        msg = ":gun: | You insert {} bullets, give the barrel a good spin and put the gun against your temple... \n:persevere: | You take a deep breath... and pull the trigger!".format(bullets)
        if random.randint(1,7) <= bullets:
            msg += "\n:boom: | You weren't so lucky this time. Rest in peace my friend."
        else:
            msg += "\n:ok: | Looks like you'll last the night, hopefully your friends do too."

        await ctx.channel.send(msg)

    @commands.command()
    @commands.cooldown(3, 5, BucketType.user)
    async def lotrfact(self, ctx):
        """Prints a random Lord of the Rings fact. 
        
        {usage}"""
        choice = random.choice(self.lotr_list)
        await ctx.channel.send("<:onering:351442796420399119> | **Fact #{}**: {}".format(self.lotr_list.index(choice) + 1, choice))

    @commands.command()
    @commands.cooldown(3, 5, BucketType.user)
    async def pokefusion(self, ctx):
        """Generates a rich embed containing a random pokefusion.
        
        {usage}"""
        async with aiohttp.ClientSession() as session:
            async with session.get("http://pokemon.alexonsager.net/") as resp:
                soup = BeautifulSoup(await resp.text(), "html.parser")

        image = soup.find(id="pk_img")["src"]
        name = soup.find(id="pk_name").string
        fusion1 = soup.find(id="select1").find(selected="selected").string
        fusion2 = soup.find(id="select2").find(selected="selected").string
        url = soup.find(id="permalink")["value"]
        
        embed = discord.Embed(title="<:pokeball:351444031949111297> __**{0}**__".format(name), colour=discord.Colour(0x277b0), url=url, description=fusion1 + " + " + fusion2)
        embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")
        embed.set_image(url=image)

        await ctx.channel.send(embed=embed)



def setup(bot):
    bot.add_cog(Social(bot))
