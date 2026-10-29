# Claude Dashboards sync

- **Date:** Oct 28, 2026
- **Participants:** unknown in the source. "Me" is Will. "Them" is more than one speaker: Justin is addressed by name, and Adrien (written "Adrian" in the transcript) is referred to. Which "Them" line is whom is not marked.
- **Source:** pasted transcript. Speech-to-text noise is left as captured ("Kube" for Cube, "Cloud" for Claude, "Morph Global demo", "Peter Snowflake spiff" and similar garbles).

## Transcript

Them: But not all the way there. You know, I think that is like the— that's kind of the stance that we want to put together here. It's like Because at the end of the day, there's obviously stuff that's still missing. You can't contribute to Kube or dbt as an end user.
Me: Mm-hmm.
Them: And you're missing all like the foldering and permissioning. And all that stuff with Claude artifacts right now. But is missing that worth $36K? And that's kind of like the question that we have to just ask ourselves.
Me: Do we Yeah.
Them: Okay.
Me: Go ahead.
Them: No, I'm thinking out loud about whether Maybe we ought to just Focus less on the actual deliverable. Like artifact right now and focus more on just writing the story out and then we'll package it as either internal or public-facing. So, you know, like you said, Justin, just even writing out end-to-end, like Up until here, it works great. From here onwards, it doesn't. This is why. And then kind of bringing Omni as like a parallel path and saying, this is, this is the story like we've tested.
Me: Sure.
Them: We'll spin it a certain way for Anything we might do publicly, and we'll obviously have a more open conversation internally about enabling SEs on it.
Me: Yeah. And I think we have a lot of the building blocks. Already. To put together that story from just like trial and error and going through all of this too. It's just a matter of how do we want to, uh,
Them: Mm-hmm. Yeah.
Me: How do we want to convey it? We can take a first hack at like Internal facing, like, this is what we tried here, diagrams of like where it falls short. Shortcomings, where Omni's good. Where it's still like a valuable, like, I mean, if we're playing devil's advocate, I set this up with Cube and, uh, It's pretty solid. I mean, like, I have to go in there and point Claude code at my, like, Kube environment, but shit, it can.
Them: Yeah.
Me: Deterministically kind of like write SQL and hit Snowflake. It's good. Like, all my questions got answered very, very consistently and accurately. Um, but it's, it's the small little gaps that, um, that we would need to like convey or like write into like a message.
Them: Yeah, I mean, does it deterministically hit cube every time?
Me: Yeah, it hits Kube. Well, I've all— I set up my Claude, so everything is off except for Kube. So there is no other route to go but Kube.
Them: Okay. I stay. Okay, so it only goes through cube basically. Yeah.
Me: Yeah.
Them: Yeah, and I think that's— sorry, go ahead, Justin. No, I was going to say that I think that makes sense and I think that is appropriate. And the other challenge is like, does it mean you can't do all views and fields? Can you query stuff that's like, yeah, can you query stuff that's not defined in Cube if you do that?
Me: Like from Um, That's a good question. My assumption was just it mirrors whatever's in Snowflake. Like automatically, so it's not making up. Any fields? Is that what you're saying? Like, If it's not in the— if it's not— if it— yeah.
Them: Like, are any of the schemas we have in Snowflake not modeled in Qube today that you could just ask a question about and see if it
Me: Go ahead. Yeah. I need to, I need to see.
Them: It's kind of silly, but now we're like counter-selling what Omni used to do. It's like, oh, well, now we can do all these in fields and you can write raw SQL. And that used to be like what we used to shit on as like a product that we didn't like.
Me: I kind of just Yeah.
Them: But now you can do it.
Me: Yeah.
Them: Um, Either way, guys, like I do agree. I think first iteration of this, we don't have to— we don't— it doesn't have to be finalized before we start catching the team up on what we've been doing. Yeah. I didn't even think tomorrow, if the two of you just like real quick, just show it off, be like, Here's the state of it right now. It's obviously not the final state of what we want to show.
Me: Yeah.
Them: But here's the initial findings so far. It's pretty good. There are some gaps. Just have a quick Hit list of here's some of the gaps that we're going to try and tackle next and what a final deliverable actually looks like. Here's obviously some material around it. Like, I don't think you need to have a whole slide deck ready to show. I don't think we need to— we don't need like all the hit points and all the things, but Even just gathering people's initial feedback behind this of like having them throw questions at you like I just did.
Me: Yeah. I like the feedback.
Them: Yeah, well, can you do this? Can you do that? Well, that looks great so far, but can you query stuff outside of Kube? Is there a— is it like, you know, does Kube have the equivalent of topics? You know, like, is there a good connector for that to drive it into like a piece of dashboard on the front end? Like, if you actually connect through a dashboard, does that reliably, you know, hit a Kube semantic object? Like, These are just like some things I have top of mind, but I think like if we present what you guys have done to the broader team, I want to crowdsource questions and that helps you guys kind of iterate on the next step there.
Me: Yeah. Yeah, play devil's advocate to our devil's advocate case and just try to break it apart. But yeah, I feel like, yeah.
Them: Yeah. You guys go shit on Omni and then we're going to tell you guys why you guys are stupid for doing so. Yeah.
Me: Yeah, I mean, like, I think, like, personally, I've been in this Enough to where like it would be nice to have an outsider's view of like things that like exactly like you said, like, and thought about. That I could take back. But yeah, that sounds good to me.
Them: Yeah. I'm starting to cheer for this.
Me: Yeah, I mean, it's, it's the cube thing is pretty nice. It's nice and like you can update it very, very quick and you can do everything you want. It's just like there's a lot of gaps, but Mm-hmm.
Them: Yeah. But who updated? Yeah, exactly. I think the meta, like, what's really, for me, the takeaway from this whole exercise is not Whether or not it can be done, it's what it takes to get it done. Because like, yeah, you know, Will, you're a team of one, you can do this. Your Kube is locally hosted. It's like not a big deal. You know, connect to Snowflake with a PAT, you can clear a lot of hurdles, but could you do this?
Me: Yeah, exactly.
Them: Across a 30-person team, that's where we're going to really see big, big pain, like, you know, big value proposition for Omni. So yeah, we can put some level of effort that you guys have taken on this too, just like an estimate of like We each went off. We've been at this for about 2 weeks. We've spent like We've met every single day together, but we've also spent outside of that X number of hours just building on our own.
Me: Yeah.
Them: Here's where we are so far. You know, like that is, um, I think that's fair. And like the bigger question is also like, don't just think about the initial build, but maintenance and like how duct taped together is this really?
Me: Yeah.
Them: Um, And like the thing we always sell that's hard to sell is like, what is the scalability of this if we wanted to? Change stuff, so. Add a new metric. Who has to do that? It's still going to be you guys. Like, If something breaks, how do we make sure that nothing downstream breaks off of that? And then of course the whole, not even open the can of worms of things like row-level security, data security, OAuth into Snowflake with a token, like that's all That's like all a separate. You know, like probably next step down the line, but I do think everything that like you guys have built so far. I do want to try and get ahead of the team just to have them like throw spears at you guys first so you can, you know, start figuring out what to build against next, you know?
Me: Yeah.
Them: I think the good news is everything you just described, it's been part of our criteria we sort of started from. So even just the last day or 2, I've been wrapping up my own dbt testing and just having Claude help me. Think about everything we learned and kind of match it to some of that to like more qualitatively describe, you know, how difficult was it, how much effort did it take. That's the stuff I want to package together. So yeah, I like the idea of tomorrow maybe Asking for a little bit of crowdsourcing. I candidly don't think there's much to show because a lot of it is just still like Claude conversations. So visually won't be a whole lot.
Me: Yep.
Them: But I think I'm fine to open it up and just say like, what are questions top of mind for people that we could go and dig into the next? A little while. Yeah, I mean, at the end of the day, it is like a Claude dashboards project that drove all this. So if you could just build a Claude dashboard in there. And then just do a little bit of surface-level digging of like what actually drives the queries like that would be helpful. Um, But like bigger, bigger picture, I'm thinking, let me know if you guys see it the same way. It's like Let's do this first call, crowdsource the rest of the team during the weekly solutions meeting, have people throw spears at you to try and figure out You know, what you need to defend against as devil's advocate, and then we want to be able to put together some sort of deliverable eventually. Don't know exactly what that's going to look like yet. I think it's okay to tell the team we don't know what it's going to look like yet, but at a high level, like the goal of this was to approach it from both lenses. Number one, from a partnership lens. Number two, from a competitive lens. Not that Anthropic thinks they compete with us, but people do view it as like a potential replacement. So it's like both from a competitive lens and from a partnership lens, here are the reasons why we're better together. Come up with material around that. And then here's the reason why, like, we're better if you try to do it, or here's the stuff you're still missing if you do it on your own. Yeah, like a slide deck will be probably part of it. And then beyond that, like, You know, just an actual full end-to-end demo of what your deployment looks like, I think. Mm-hmm. Does that make sense? Yep.
Me: Yeah.
Them: Well, do we feel good about tomorrow then?
Me: Just like initial demo and talking about it and crowdsourcing. Yeah.
Them: Yeah. Yeah, this is what I've done. Here's the level of effort so far. If you can, between now and tomorrow— is it a morning one tomorrow or is it an afternoon one for us? Okay. If you have the chance between now and tomorrow morning, just real quick, dropping like a Just ask it to create a dashboard of whatever dataset it is, just so you can feed it like a screen, feed it like a screenshot of the demo that you built it off and just be like, recreate this dashboard. And then let's just dive a little bit into like
Me: Yeah, morning. Okay, I'm gonna do that right now.
Them: And, you know, the experience to dive deeper and all that stuff, which like we know Omni is really valuable for. And then after we crowdsource the devil's advocate to the devil's advocate questions, then we can say like what a deliverable is probably going to look like the following week. Is a slide deck that shows both better together and competitive. And then along with that, an actual Morph Global demo. So probably like a 2-banger back-to-back week type thing.
Me: Mm-hmm.
Them: Yeah, I just feel like you guys have been building in a silo for so long. I want to see other people, like, number one, just give you guys some credit for doing it. And then number two, making sure that we're taking a good direction that's going to be valuable to people.
Me: Yeah.
Them: Yeah, I think what's interesting with this is like the outcome of it is, is it less demoable? Meaning we're not enabling the team to go set up their own full end-to-end like Cube example, but it is just like— Nor do we want them to. Yeah, sure, exactly. Yeah, like this is a story you should be able to tell. Yeah. And like, you can use our learnings as the foundation for this pitch you're making, but like, we've done all the work to give you confidence that This is the talk track and it resonates. Yeah, I mean, I think the idea we had like last week too was like go through what you normally do in a standard Omni IBI demo. And try to do each of those same things with whatever you guys build. Ask a question with AI, it's going to be able to do that. Can we open that in a workbook? No, there is, there is no— you can ask it to build a dashboard from there, but can we open it from a workbook and play with the UI? No. Is there a place we can put Excel functions? No. Can we contribute back to the semantic layer. No, we can't, we can't do any of that. So it's like, that's the type of stuff where it's like, hey, I'm going to walk you guys through as a piece of material, both a slide deck and alongside the slide deck. Here is us trying to demo. The same stuff we demoed Omni with this best-case scenario deployment of yours. Here are all the things that are still missing.
Me: Yeah.
Them: And it's like, don't, don't go recreate a whole UI for like a workbook, but like that's something that someone would have to do. That's an absolute pain in the ass to do.
Me: And I, yeah. I was, I was gonna say like, there is an angle of this where like, it could be Adrian and I's full-time job to go off and try to literally make every single aspect and try to like duct tape everything together that We're just like not going to be able to do, but I think that goes back to like even Adrian's point this morning that he told me with the semantic layers or like another integration that you would have to do with dbt where you're now paying and you're now managing it. It's like those little things of like build versus buy. Yeah, we didn't go out there and like recreate Omni with every interface, but Those are the gaps that you would have to go off and manage yourself and probably pay money for too.
Them: Yeah, yeah, like this is assuming everything you did is free.
Me: Yeah. Yep.
Them: And if it gets to the point where you have to go buy a tool, to get access to what we've done anyway, then you might as well buy Omni. Then at that point, the point is moot. So it's like we've done everything here intentionally with open source, number one, so Jake's not mad at us, but also number two, like if it requires you to go buy a paid license of Kube, or go buy dbt semantic layer, which used to cost money, then like at that point you might as well just do what we've already done.
Me: Exactly.
Them: You know, like that's, I mean, might as well just buy Omni. So like, I think you guys are taking the exact right approach to this and the immediate step for tomorrow is just to like show off what you've already done so far.
Me: Yeah.
Them: Initial findings. If you just put, it doesn't have to be a full deck, maybe just to have like a single slide, here's what we've already done. This is what's easy. Here's what's hard. And then everyone will throw spears at you. And then the next step from there is to do like a broader deliverable. And if you want me to start it off and set the stage, I'm happy to do it too. But I think like I just want to make sure you guys get some credit here.
Me: Yeah. Okay.
Them: Yeah, I'm planning tomorrow just being a super open-ended conversational, like what are people getting asked right now and Just like dump a bunch of questions to us and we'll take that and go. Go find answers for you. Yeah, don't need— doesn't need to be super process heavy, I think, for tomorrow.
Me: Yep.
Them: All right, let me make sure we get you on the calendar for tomorrow. Uh, we are, we're always Or I was running out of time. Oh, Ariel shares roadmap, Peter Snowflake spiff, Bernard Coco, Jonathan Snowflake performance feedback, Jesse App Gallery, good.
Me: Oh Lord. Oh no.
Them: Lord.
Me: I don't know if it makes
Them: Um, If it works, it works. If not, we'll combine both into next week's. Yeah, okay, I will.
Me: Sure.
Them: Post something in the meantime if it's really okay.
Me: Those seem important too.
Them: Impressing. Let's say like, oh yeah, I mean, Peter's and theirs might be very, very quick. Let me just tag Lara in our internal thread real quick. Well, while you're doing that, I think we'll, um, I'm going to start just like taking all the chats in which I've asked it to answer those 10 questions. I'm going to go into each one and paste like a build me a Claude dashboard out of this. And then just start looking at that a little bit. Because, you know, the consistency angle of the BI piece and like, you know, we've done all the part that is, can you get the answers? Now, can you just build me an artifact that is consistent, shareable, all that? So
Me: Oh, that's a good point too. Should be just one prompt on the session that we were doing at the very end to just say, build me a Claude dashboard. But yeah, cool.
Them: Yeah. I'm just going to copy paste the same prompt and start that angle a little bit. But at least it should give us something for tomorrow to Justin's point. And then it also gives us a good start into the BI evaluation piece of this when we want to tackle it.
Me: Yep. Yep. Cool.
Them: But I just asked it right now and it failed to load every single query. Now I got to figure out why, but that's a learning. Yeah, it's like every single demo we show, we click the Compass button.
Me: Good. Side note. Yeah, yeah, go ahead.
Them: Like every single demo, you ask a question to AI, Compass button, open in a workbook, explain this, explore this. Like that's the type of stuff I anticipate being really hard to do. So you have to like rebuild the entire UI behind.
Me: Yeah. Yeah.
Them: Um, Laura says that yes, looks like we're going to try and push a couple people. How long do you think you're going to need?
Me: 10, 15 minutes. Yeah.
Them: I don't know, 10 minutes. Yeah. People might have no questions, people might have a lot of things to say. So I think aim for 10-ish, 10, 15. Well, I'll say 10, 15, 20 minutes with questions, people open-ended. And yeah, I think the way just to set the stage is like, this is not the final deliverable. Just wanted to start talking through what we've done so far. We want you guys— if we've been playing devil's advocate, we want you guys to play Omni advocate against us. So what else do we have to go and try to build between now and next week to bridge the gap that Omni provides?
Me: Yeah.
Them: Like that. Cool. All right, well, thanks for the brainstorming session, Justin, and keep you updated on progress towards next week.
Me: Cool.
Them: Thank you all. Appreciate it.
Me: Yeah. Thanks.
Them: Nice work, both of you. Seriously, really good stuff.
Me: Yeah.
Them: Thanks. All right.
Me: See ya.
