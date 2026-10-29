# Will / Adrien - Hold

- **Date:** Oct 26, 2026
- **Participants:** Will Clayton, Adrien Beaufils
- **Source:** pasted transcript. In the transcript "Me" is Will and "Them" is Adrien. Speech-to-text noise is left as captured (for example "Kube" for Cube, "Cloud" for Claude, "Tim" as a name at the end).

## Transcript

Them: It on Thursday, he turned around this like Acme demo thing on Snowflake that I basically have been using as my.
Me: Mm-hmm. Okay.
Them: My demo thing. Made some roles. Made a dbt, well, basically like I had him, you know, help me with that. Then I got just Claude and I worked a bunch to go through all of the like You know, create a dbt project, create a repo. Push some stuff into it, log all the kind of effort at each step. Um, On the Snowflake side of things. There's some nuances there that like maybe it'll be relevant if we go and talk to the team about it, but basically like I'm limited by the ability. To connect. Because what I want to do is simulate an environment in which the user is defined by their role at Snowflake. Whereas right now the Snowflake connector we have, the dbt role has access to a bunch of things. So basically I went and created a personal access token and I'm using that to make a sort of custom connector that simulates what it's like to only have access to that specific
Me: Mm-hmm.
Them: Snowflake thing.
Me: Okay, I think I did a similar thing.
Them: So
Me: I'm so mixed up. I got a lot of moving parts. I'm like,
Them: Yeah. No, same. I'm not done. So like once I am, I'll have, I'll have like a summary of kind of what's going on. Where I'm at right now, just to give the update, is Basically, I'm at the step where I have the same like 10 questions.
Me: Yeah.
Them: That I ran in Claude, and each time it's using that Snowflake dbt output. To try to answer. And so I just like wrote the answers in a doc, had Claude tell me like how successfully is it being consistent and all that, because then the natural next step is, well, if you equate that to Omni, You would want to make a change and you would want to promote that and like see if it changes things. So that's what I'm trying to have it do right now.
Me: Okay. Yeah.
Them: None of it is related to Claude dashboards yet.
Me: Okay.
Them: It's kind of the underlying like Before I even made a dashboard, how— yeah, it's like, how would I know that the number comes from the right place? And also, what would I do to like make a change if it wasn't right? So that's where I'm at. I'd say next steps are like figure out that process, keep documenting it, and then basically get to a point where I can be like, okay, this is a representative semantic layer through dbt. Now let's just throw a couple of dashboards on top of it.
Me: It'll eventually get it. Yeah, it'll— yeah. Sure.
Them: And just like do the last mile piece.
Me: Sweet. Okay, that all makes sense. I guess questions.
Them: Right. Mm-hmm.
Me: I'm in a similar spot too, to where I I think my next step is getting those 10 questions in, in like Not like fabricating wrong answers of like, Hmm, I'm like trying to figure this out with, with Cube too, of like, hey, if you have 10 answers and it gets it wrong, Go into Cube, change this metric, and then like Run it again and it'll be correct. Like, What are you thinking as far as Like questions, and are you like purposefully doing it to where like maybe like dbt couldn't answer it that like Claude or that Omni could like? You know what I'm saying? I foresee the only difference between if you ran it through Omni and you did like the Snowflake dbt route that you're doing. They're both going to get to the same answer. At the end, if you put the context and the description and stuff behind it, or that's what I'm foreseeing, is it just like the effort difference of like having to manually go in and change the dbt and do all this stuff and rerun it again that We're thinking is the difference, because you could, I mean, unless it's like a really, really complicated question, but even still, like, I think you're going, if you give it enough context, you'll get the same answer in both routes, you know?
Them: Yeah. Yep.
Me: How are you thinking about that?
Them: Yeah, correct. Correct. So, um, I'm looking for Uh, yeah, so let me show you this. So basically I had Claude. At some point here, come up with These 10 questions, like it, they just made these. Honestly, I did not like iterate on it. I just, I was like, whatever, these are fine. But I think what's interesting is you have like very easy questions.
Me: Nice.
Them: Then you have stuff like this, a bit more nuanced. And then like, to be clear, some of these do, they, there is a little bit of like, okay, we just have to filter, et cetera. It's not just one number. So not complex, but at least like could be potentially misinterpreted. And then there's these 2 that I added, which I think are good. These are not things that should be able to answer and we, we want it to fail. That is also a success criteria is like, It refusing or it having no access. That's more on the
Me: Right.
Them: That's more on like the roles and Snowflake connection side of things. But I mean, if something is enforcing a loose restriction or loose permission where like me prompting it hard enough could go around dbt, then that would be a problem. So anyway, it made these. I basically then Because I'm in Cloud Code here, went into Into regular Cloud Desktop. And I turned off all of my connectors except this new one that I made, and then just pasted every question and like Took the SQL here that it wrote and the answer and put that in a Google Doc. And then I handed it back all to Claude and Had me like kind of think through The output. So what's interesting in this and how I kind of look at it is There's the consistency and accuracy angle of this, which we can measure, like how many of these did it objectively get right? And then there's the Okay, well, if it's not the same, what do I do about it? Which is the next angle I'm trying to investigate. But for example, this Q7, which was the repeat customers, It did it differently.
Me: Mm-hmm.
Them: And it also did it differently than what our canonical answer should have been. So The idea, like what I'm kind of working on now is what do I do about that? And that's where we're thinking about like ultimately what is the flow? Sorry, it's a better diagram of like What does the flow look like? To, um, To go make the improvements. So Where was this? Where was your initial question? I forgot.
Me: Yeah, I mean, you answered with the 10 questions, like, how are you basically like testing that? And then like, how would you test the change? And it sounds like you're kind of in the testing the change in like the level of effort it would be to.
Them: Through my response, but Yeah. Yeah, correct. There's, I'd say like, again, the initial pass was just a matter of Consistency. So without any change, with nothing being different, can we achieve A pretty, like, a high enough level of consistency. The next thing is, okay, well, now what do we do about this? Like, what does the iteration process look like? And then I agree with you, it's, it's actually not going to be I think at the end of the day, you can probably do just about everything in here you could with Omni, is what you were saying, and I agree. If I wanted to change the definition and make sure that Q7 gives me a better answer, I'll probably be able to make that happen. What's more interesting is the amount of effort and all the handoffs and touchpoints that need to happen. Which in my case means We're going to go create. Some like dbt thing. But as Claude was telling me, it's actually not even It doesn't make Claude use it. Like, that's— these are, these are the trade-offs we're actually wanting to tell a story around at the end of the day. It's like, I can make these things possible with this approach, but can I make them as sure and governed And enforce as Omni? Probably not.
Me: Nice.
Them: So.
Me: Yeah.
Them: Anyway. I don't want to skew your stuff, but I can also send you these questions if it does help to me make The analysis comparable.
Me: Yeah.
Them: You let me know.
Me: Yeah, I was. I Slacked you and I went into this dashboard and this is like, Again, a nice failure. It's annoying because it's a failure, but it's also like, Nice because I had to like set up a certain thing for Kube and host it in a certain area and then like create like a custom tunnel in order for like all of this to work. And the tunnel went down to where I hit the refresh on the dashboard and everything broke. Because these little custom things weren't like in place. So I'm at the point where like everything's broke. I still have a lot of like stuff like documented out. I am trying to Consolidate everything into like one cohesive thing. Like I've tested a bunch of different things, but I'm trying to make it like one singular doc, like similar to what you were showing as far as like Here's the level of effort it takes to set up. Here's the questions that I ran through it. Here's the level of like manual effort. Now that this is broken, I might flip over to the same Snowflake that you're using just because it's everything's already broken, and I guess I could just like start from, start from there too.
Them: Mm-hmm. Hmm.
Me: Um, And then yeah, my next step would be go in. Just test the manual things with Cube and then run it through like another set of like 10 questions or something. But that's like similarly where, where I am.
Them: Okay.
Me: It's, uh,
Them: Gotcha.
Me: Yeah, this one's a weird one. I assume that dbt is in some sort of like Git repo or something, right? For on your end?
Them: Yeah, but I'm in my own repo. I don't want to like merge it or model anything else. So everything is more or less self-contained here.
Me: Fine, yeah. Okay.
Them: Acme Snowflake. My own dbt repo that pulls from that Acme Snowflake and actually puts it back in there as a dbt my name Mart schema.
Me: Cool. New table.
Them: And there's only 4 tables that output: customers, products, order items, and orders. And that's, that's the full scope of what my role has access to.
Me: Cool. Yeah. I'm hitting a point where I have like Kube like locally running in my Docker, I cannot figure out a way to like I think just like with the way that Kube is set up, like you either have to like host it like locally in order for it to be free, or you have to have like Cloud Kube, which is money. Like all that to say, like I can't put it in a repo because like that's not the purpose of it. And like if I need to go in and change something, like I have to go through my own, like I have to make sure that Docker's running. I go into Kube, I change, do whatever I need to do. So that's like the issue that I'm running into right now. Which again is like a good failure because Claude is having a tough time with like the custom connector. To Kube that eventually feeds Snowflake. That's where everything kind of just like blew up. Um,
Them: Hmm.
Me: Because I guess like how Kube works, my interpretation is it's like kind of what Omni's doing on the backend. Where It's not like deterministically doing something. Like, how can I explain this? My fucking head is all over the place.
Them: Yeah, it's, uh, it's kind of tough to make sense of it, but
Me: Yeah. I'll try to figure it out, but what you just showed, if you want to share that repo or just like the link to the repo so that I could have the, uh, The questions too. And maybe some, like, the methodology might be like a little bit different with how this Has to operate, but
Them: Mm-hmm.
Me: Yeah, let me Let me share my screen and show you. This is more so like what I'm thinking as far as like Success criteria and like Setup, hosting. Data engineer, what happens when you need to change a metric? Safety of like, are you breaking anything? Permissioning.
Them: Mm-hmm.
Me: Like the interface, are you doing it in Cloud and having to adjust things and switch tools and do all this stuff, or is it in one singular place with Omni? These are more, more so like the things I was thinking of like testing against. Um,
Them: Well, what's good is that I think the way we define our criteria, anything that is Dashboard specific. Is agnostic to whether it's dbt or cloud or, sorry, dbt or Kube or whatever is underneath. So I think we should, at some point, you and I will need to get together and cut over from this current work into just testing the dashboard BI aspect. So I would say don't go into that. Yet, or, or if you do, maybe keep track of it separately because it's not a cube-specific thing.
Me: Cool.
Them: Right, so I don't wanna.
Me: Yeah.
Them: Do, you know, have you do extra work, or if you do, then like, I think what you find also will be applicable to my work is another way of putting it.
Me: Yeah, I'm like, Trying to test a bunch of different things of like, hey, like go out and change this or add this or connect to a new table. Almost just like brain dumping everything I can into this repo with the intention of like, here's what I tried here. Like, I think I have like a whole like findings page of what's going on, like any, any sort of learnings to what's going on. It's more like, how do I make sense of all this junk that's outputted?
Them: Mm-hmm. Yeah.
Me: Yeah, this is great. I'm having it go like, you know, here are lessons. On various dates and just kind of brain dumping it. But what to do with it is, is the next. Is the next step on my end.
Them: Mm-hmm. Okay, yeah, I think Let's see, where does, where does the separation kind of live between What we're testing versus getting to the dashboard piece, because Let me pull up the criteria real quick. I'm gonna just live brainstorm which of these I feel like I've gotten to so far.
Me: Yeah.
Them: And you let me know as well for your side. But also one thing that I need to think about is I'm so far testing just regular dbt, not dbt semantic layer. That's probably an angle I also should visit.
Me: Okay.
Them: At some point here. But anyway, so So looking at this, like setup effort, I feel like I'm getting pretty well documented here. Maintainability.
Me: Yep.
Them: Scalability, centralization. I think there's all of that is happening. Obviously, I need like condensed learnings, but just a general sense for what does it take to get this off the ground? Who are the personas involved? The diagram I barely showed you or briefly showed you I don't love, but I'll make it better. The idea of it though is it was showing based on coloring what step pertains to which type of user. So is it a cloud admin? Is it a Snowflake admin or whatever? And I think that's also a bit of the story here of this admin stuff.
Me: Yeah. Yep. Yes.
Them: So I feel like I'm getting pretty good at covering this basis. On the rest of this, as I think where I'm at right now, so accuracy and consistency, those are the 10 questions. That I've been running. The Auditability I've not thought about, but basically that happens organically by just like the query ran was a SQL query and could I have looked at that? Or not, like depending who I am.
Me: Sure.
Them: What I'm probably most focused on testing next would be improvability. That's the piece of like if I were to change That definition somewhere in dbt, what does it take? And then also like maybe rerun the same test, see if it made a difference and all that. And a couple of these. I'll look into as well, but like cost might just be a matter of how much it costs. Like how many credits in Claude or that kind of thing.
Me: Sure.
Them: So I think I'll be roughly speaking, through kind of this top section or these top 2 sections, hopefully within a day or 2 here, and able to start pivoting towards just packaging the learnings from it and then Either maybe tack on the semantic layer version of this testing, or maybe just get back together with you and pivot to the Claude dashboards.
Me: Jump, jump to dashboards.
Them: Yeah.
Me: Gotcha. Okay.
Them: What are your Impressions? Where do you feel like you're at?
Me: I'm, I'm, yeah, I feel like I'm good enough on Yellow portion as far as just like documentation of what I've done. Accuracy, consistency, like that's where My next step is, um, with those 10 questions.
Them: Yeah.
Me: And then, yeah, like how, how I guess like on top of that too, like how easy is it for me to Change something and then run that again, or like who's involved with that? I have the idea, like I have that documented. It's actually like running it through like tangible questions too. Um,
Them: Mm-hmm.
Me: Haven't. I think one of my big gaps right now is like security and making sure that certain people can only see Certain portions of the data. I think that one's going to be a little bit trickier because I think you can set up like profiles and stuff within Q, but then like, I don't know how that really works with Claude as That's, yeah, that's a gap for me. Um,
Them: Mm-hmm. Well, that would have to do with your— how you're connecting to Snowflake, no?
Me: Yeah, I guess like looking at it from the Omni perspective of if you have a service account and you connected it to Snowflake, but you're attributes or whatever are within Omni, it's almost like if your attributes or something was stored in a profile in Cube to where it's like, oh, like this user is running through this Snowflake, but they only have access to see a certain thing in Cube, therefore they're going to only get this output. That's one route, but you could also, I guess, chalk it up to like there's no security, it's just whatever connection you have configured with Snowflake. That's one route, but I
Them: Mm-hmm.
Me: But yeah. I might need a cup. Yeah, go ahead.
Them: Well, let me do this. I'm asking Claude right now to package up. The questions, I did those 10 questions, and then also the Snowflake setup. So Then I'll send it to you, and if it's at all helpful and possible to, uh, To connect to the same stuff, that would give a pretty good basis because I think some of what you're describing maybe is already taken care of by Again, for example, the fact that here I have a connector where I'm using a specific role and that viewer role has only access to a schema.
Me: Okay.
Them: That we want, like my— in my case, a dbt schema. But that kind of takes care of some of this. And of course it doesn't have the full like row-level security and all that, but maybe I'll send that to you.
Me: Sure.
Them: If it's helpful, use the parts that you can. If it's not, then like keep doing your own thing. We'll reconcile it wherever possible.
Me: Okay. Yeah, that sounds good. Yeah, I'm thinking of the— I'm just kind of like reconciling like right now of just like getting on the same page so that we're all— we're both like working off of one thing.
Them: Mm-hmm.
Me: Yeah, if you want to send that over. I'll try to get that Snowflake connection set up too. I don't know how I was doing it in the beginning. It was like a lot of trial and error. I feel like I was making my own token or something somehow, because I was getting like a permission denied or something when I was initially trying to do it. Through whatever roles in Snowflake. So that might have been my workaround. But if you have something already set up with Acme to where it's like Yeah, we can just connect and do it that way then. Then I'll just go that route.
Them: Mm-hmm. Okay.
Me: Cool.
Them: Cool, cool. All right, we We'll need to provide an update probably because I think Justin had wanted something by Thursday. I— it may be in our best interest to look at next week in order to have something more polished put together than just A semi-completed thing.
Me: Yeah. Yeah.
Them: But Let We're talking to— I think we have more time tomorrow, so if that still works, we should probably just keep chatting and
Me: Okay. Sweet. I was like, I gotta My calendar's filling up tomorrow, but one of those is a one-on-one with you. So cool.
Them: Yeah, yeah, yeah. So Let's keep that on the books and then maybe I'll shoot Justin a note end of day here just to keep him up to date. And we'll see if, uh, If you want something by Thursday or maybe next week is a better goal.
Me: Cool. That works.
Them: Cool. Alrighty, well, Back to it, back to the Cloud.
Me: Back to it. Running out of Claude credits. I feel like I keep hitting the request to request for more credits, but It is what it is. I'll keep doing it until I get a Slack from Joe or whoever owns it.
Them: Yeah, well, hey. Yeah. Yeah, yeah. I mean, look, at the end of the day, like, we're testing the edge on this stuff. If you and I can't get credits for it, then no one can. So Alrighty.
Me: Yeah. Yeah, that's true.
Them: Well, Talk to you tomorrow then.
Me: Cool. Talk to you later, Tim.
Them: Yep. See ya.
