import hashlib
import traceback

import bittensor as bt
import requests

from neurons.miners import index_data
from neurons.miners.utils import hash_code


def head_tail_api_pred_human(list_text, urls, timeout=12):
    try:
        results = []
        for i in range(len(urls)):
            result = head_tail_api_pred_human_with_url(list_text=list_text, url=urls[i], timeout=timeout)
            results.append(result)

        preds = [False] * len(list_text)
        for i in range(len(results)):
            for j in range(len(preds)):
                preds[j] = preds[j] or results[i][j]

        return preds
    except Exception as e:
        bt.logging.error(e)
        traceback.print_exc()


def head_tail_api_pred_human_with_url(list_text, url, timeout=12):
    # bt.logging.info("head_tail_api_pred_human list_text :" + str(list_text))
    final_human_pred = [False for _ in range(len(list_text))]
    not_touch_index_list = []
    input = []
    for i in range(len(list_text)):
        text = list_text[i]
        if len(text) <= 250:
            final_human_pred[i] = True  # Human text < 250 chars
            continue
        list_token = index_data.cut_head_tail(text)
        if len(list_token) == 1:
            final_human_pred[i] = True  # Human text is short
        else:
            not_touch_index_list.append(i)
            tmp_data = []
            for token in list_token:
                m = hashlib.sha256(token.encode('UTF-8'))
                sha256_hex = m.hexdigest()
                hash_value = hash_code(sha256_hex)
                db = hash_value % 10_000
                key = sha256_hex[:8]
                tmp_data.append(db)
                tmp_data.append(key)
            tmp_dic = {
                "head_db": tmp_data[0],
                "head": str(tmp_data[1]),
                "tail_db": tmp_data[2],
                "tail": str(tmp_data[3]),
            }
            input.append(tmp_dic)
    if len(input) == 0:
        return final_human_pred
    body_data = {"input": input}
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, json=body_data, timeout=timeout)
    if response.status_code == 200:
        data = response.json()
        human_pred_result = data['result']
        for i in range(len(not_touch_index_list)):
            human_pred = human_pred_result[i]
            not_touch_ind = not_touch_index_list[i]
            final_human_pred[not_touch_ind] = human_pred
        return final_human_pred
    else:
        print('Failed to post data:status_code', response.status_code)
        print('Failed to post data:', response.content)
        return []


if __name__ == '__main__':
    urls = ["http://69.67.150.21:8080/check-exists",
            "http://103.219.170.221:8080/check-exists"]
    list_text = [
        'They are known for their controversial music, performances, and political activism. The group has been involved in various protests and demonstrations against the government, particularly on issues related to women\'s rights and LGBTQ+ rights. Recently, Pussy Riot has been making headlines due to the imprisonment of its members. The group\'s vocalist, Maria Alyokhina, was sentenced to two years in prison in 2012 for her role in a protest against Russian President Vladimir Putin. Another member, Nadezhda Tolokonnikova, was also imprisoned in 2012 before being released in 2017. The group\'s music and activism have been criticized by some as offensive and disrespectful towards religious institutions. In 2012, Pussy Riot performed a "punk prayer" inside Moscow\'s Christ the Savior Cathedral, which led to their arrest and subsequent trial on charges of hooliganism. In summary, Pussy Riot is a feminist punk rock group that has been involved in various protests against the Russian government, particularly on issues related to women\'s rights and LGBTQ+ rights.',
        'The chimp is indeed in the area where where the bubbles are. The area is in which the bubbles are is is in the area where the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in the area in which the bubbles are is in',
        'WLOY will be there spreading cheer and handing out some wonderful kids sweatshirts! That’s right KIDS SWEATSHIRTS! We are prepared to keep merry and warm on Sunday! Come out and see our van in special Christmas attire. I can’t tell you what the WLOY van will look like on December 7th because that will ruin the Christmas magic. You will just have to come and be surprised! It will be like an early Christmas present from us, WLOY!',
        'Every workday from 2007 through 2011, I took a bit of a journey to get to work. I’d first ride a public bike to get my daily breakfast, an egg pancake made by the world’s greatest egg pancake master. I’d continue through the southern streets of the city, past the train station and a few rivers, until I arrived at 金衙庄, a neighborhood near the train station. I’d wait there with Master Fei and the gang for anywhere from a few minutes to 45 for the company bus to come pick us up. From there, the trip to the factory would take as little as twenty minutes or as long as an hour and a half (the record was set this winter, clocking in at over three hours). This is a short video I put together entirely on my iPhone 4 of the first leg: the bike ride to 金衙庄.',
        '"Bonnie \'Prince\' Billy is an American singer-songwriter and actor, formerly known as Palace Music and Palm Sunday. He\'s been releasing albums since the mid-90s under various monikers, blending folk, country, psychedelic rock, and experimental sounds. His music often features introspective lyrics and poetic storytelling. In 2001, he embarked on a world tour titled \'I See a Darkness,\' promoting his album of the same name. The tour was known for its emotional performances, which gained critical acclaim." That\'s it! Two minutes flat.',
        'The distance between (-12, 6) and (16, -6) can be found using the distance formula in two dimensions, which is given by:\n\ndistance = sqrt((x2 - x1)^2 + (y2 - y1)^2)\n\nSubstituting the coordinates (-12, 6) for (x1, y1) and (16, -6) for (x2, y2), we have:\n\ndistance = sqrt((16-(-12))^2 + (-6-6)^2)\n\ndistance = sqrt(48^2 + 12^2)\n\ndistance = sqrt(2304 + 144)\n\ndistance = sqrt(2448)\n\ndistance ≈ 49.55 (to two decimal places)\n\nTherefore, the distance between (-12, 6) and (16, -6) is approximately 49.55 units in two dimensions.',
        'A PCI (Peripheral Component Interconnect) port is a high-speed serial communication interface used to connect electronic components to a computer motherboard. Purpose:\n\n* Provides a standardized way to connect peripherals, such as:\n     Solid state drives\n     Graphics cards\n     USB controllers\n\n\nFunctionality:\n\n* Uses a 32-bit parallel data bus and a clock signal to transfer data between the peripheral and the motherboard. Provides power to the connected peripherals. Types:\n\n* Modern high-speed version with greater bandwidth and lane count. The motherboard has a PCI slot with electrical contacts that mate with the connector on the peripheral device. * The data and clock signals are transmitted through the slots and cables. * The peripheral device interprets the signals and performs the necessary operations. Uses:\n\n* Connecting hard drives and SSDs to the motherboard for data storage. * Connecting network adapters to the motherboard for network connectivity. * Connecting graphics cards to the motherboard for video processing and display.',
        "Impact on Netserver:\n\n* HP already had its own line of servers and workstations, and acquiring Compaq brought in another set with overlap in the netserver market. This redundancy caused confusion and cannibalized sales. * HP's attention was split between two competing server lines, leading to less investment and innovation in the netserver market. * Netservers were considered legacy technology by HP, which focused on newer and more profitable product lines. Discontinuation of Netserver:\n\n* By 2009, HP had phased out the netserver line due to:\n     Aging technology\n     Competition from other vendors like Dell and Cisco\n* Changing market trends towards virtualization and cloud computing\n* HP's emphasis on higher-margin products like enterprise servers and storage solutions\n\nIn essence: The acquisition of Compaq led to product redundancy, outdated technology, and declining profitability, ultimately resulting in the discontinuation of the netserver line.",
        "Last week I was able to take a vacation day and meet up with my unbiological twin, Becky. It was our first get together since she's moved back to the area! We wanted to do something fun and since the summer of 2012 when the Museum of Broadcast Communications moved into it's new 62,000 square foot building I've been dying to go visit. This was the perfect choice for the two of us. Just north of the river, the MBC is a nice little walk from most of the Loop's public transportation and just a few blocks west of the shopping on Michigan. Heading into the building you're greeted by a friend staff member of the two and a half floor stairwell/foyer area. As we took the stairs to the second floor to see the radio exhibit and radio hall of fame we came across this awesome sculpture of old TVs and radios. When you first get onto the second floor there is an extremely interesting history of the radio and how it was created.",
        "Maybe I will start watching it again. Reena answered the question Do you think the Indian women's cricket team is getting the right recognition for their efforts over all these years?. Reena answered the question Favourite Team in Pro Kabaddi League?. Jaipur Pink Pathers is my favorite team in Pro Kabaddi League. Manjeet Chillar is the captain of the team.",
        'Subtract 7 from both sides of the equation to get 8x as the only term on the left side. So, subtract 7 from both sides: 8x + 7 - 7 = 8 - 7\n2. Simplify the left side b combining like terms: 8x = 1\n3. To solve for x, divide both sides of the equation by 8: x = 1/8\n\nSo, in plain English, to find the value of x that makes the equation true, subtract 7 from both sides of the equation, then divide both sides by 8.',
        'This, I think, should be our fundamental theme of ‘Communication Engineering’. What do you say? I think it might work best for CE to look at the patterns of communication in an organization. P&G is able to have highly structured and “tight” communication that underlies their execution. At the same time they have an operation with “loose” communication as they face their customers. What I am trying to get to with “loose” communication is demonstrated by the story of razors in India. First thought was for mesearchers to visit the Indian disapora in London.',
        'Metaxas played a significant role in the resistance against both Italian and German occupation during World War II, earning him widespread respect and admiration among Greeks. The capture of Chios was also significant because it led to the establishment of a Greek-controlled state on the island. The newly formed Hellenic Republic of Chios (also known as Scio) operated independently from mainland Greece until 1922, when it was incorporated into the Greek state following the devastating Asia Minor Disaster.',
        "The very first thing I noticed was that the dealer had replaced something that I did not ask to be replaced. And it certainly wasn't on the list from the tire sshop. When I dropped off the car, I never said anything that would have led the dealer to believe that this item was in need of replacement. And he never mentioned replacing it. It was never discussed. The question is, what did the dealer do? I'll give a hint. It was not a safety recall or any thing of that nature.",
        'Pick up your medical records by visiting our customer service window during business hours. You need to show a photo ID. Or, request your records be released into MyChart. If you don’t already have a MyChart account, please contact your doctor’s office to obtain an account. Read a tip sheet about requesting medical records in MyChart.',
        "In August, 2017, the quartet will set out on this run with a vision of raising the bar to the next level, as they present a night to remember in these markets featuring a set list composed of repertoire they have never performed on stage, new material, and of course their hit tracks. Plans also include a range of surprise special guest appearances. The band has already begun creative discussions aimed to deliver a unique show with production that is their most ambitious to date. The tour will begin in Hamburg on 23 August, 2017 with multiple outdoor events planned in Germany, alongside performances in Denmark, Sweden, Norway, The Netherlands, Switzerland, and Austria. The pre-sale for all appearances cited below goes live on November 30 10AM via the band's Rebels and Angels fan club HERE. A general on-sale follows on December 1, at 10:00 AM.",
        "Robert Montgomery, Stagecoach UK Bus Managing Director, said: “The thousands of drivers across our team who have achieved Fleet Elite status should be rightly proud of their achievement. “Stagecoach’s phenomenal success is largely thanks to its focus on developing an exact methodology for the GreenRoad deployment. With well thought through processes and buy-in from all stakeholders, Stagecoach ensured it maximised the opportunity to bring about a lasting change in driver behaviour. For both business and environment, Stagecoach's results demonstrate the value of acting on the insights delivered by GreenRoad” said Andy Cozens, Director of Sales EMEA at GreenRoad.",
        "Help maintain data integrity - By using distinct PSI labels, you can ensure the correctness of the data by tracking its origin and associations with other relevant information. 2. Improve readability and interpretation of data - These labels make it easier to understand what each piece of data represents and how it relates to the rest of your program's functionality. 3. Enhance security and access control - PSI labels help safeguard sensitive data by ensuring that only authorized users can view or manipulate certain information within a given program. 4. Enable efficient storage and retrieval - By assigning specific labels, you optimize your program's database structure, facilitating quicker search and retrieval of relevant data when needed. In summary, PSI labels help in effectively managing and organizing data within a particular computer program by creating unique identifiers that represent its context and purpose. They improve data management processes while ensuring proper security measures and user access control.",
        "During his time in the Prussian Army, Duke John Albert gained valuable experience in leadership, organization, and strategy—skills that proved essential for managing colonies. Furthermore, he was exposed to the ideologies prevalent within the European powers during this period. The notion of 'the man's burden,' which held that it was the duty of Europeans to civilize non-European peoples through colonization, gained popularity among many European military and political figures during this time. Additionally, John Albert's experiences in Africa, particularly during the 1864 expedition to East Africa with Prince Adalbert of Prussia, further influenced his thoughts on colonization. During this mission, they encountered various African ethnic groups and negotiated treaties that granted Prussian influence over vast territories. These experiences helped solidify John Albert's belief in Germany's rightful place as a colonial power.",
        "Tampere has a long history, dating back to the prehistoric times when it was an important waterway and crossing point. It gained importance later on with the establishment of the city by Alexander von Kothen in 1779, under the reign of Gustav III's father, King Adolf Frederick (1751-1771). Tampere was then part of the Swedish Empire at that time and was one of many cities founded during this period. King Gustav III succeeded to the throne in 1772, after his father's death. His reign would last until 1792 when he was assassinated. Although Tampere itself wasn't established during his time as king, it continued to be under Swedish rule during that period, eventually becoming part of Finland after the Finnish War (1808-1809) and the Treaty of Hamina (1809).",
        "Charles Gonzaga, also known as Ferdinand Charles, was a Duke of Mantua and Monferrato. He supported France during the War of the Spanish Succession, which had significant consequences for his reign. By siding with France, he alienated himself from other European powers, particularly Austria, who supported the opposing side. This led to a loss of influence and power for Charles Gonzaga, as well as financial struggles due to the expenses incurred during the war. Additionally, the War of the Spanish Succession was a prelude to the more significant conflict known as the French Revolutionary Wars, which would further impact Europe's political landscape. In summary, Charles Gonzaga's decision to support France during the War of the Spanish Succession contributed to his loss of influence and power, ultimately affecting his reign as Duke of Mantua and Monferrato.",
        "This might be confusing, so let's break it down like you're five. Communism is a political ideology that aims to create a society where everyone has equal opportunities and resources. Socialism is an economic system in which the government owns and controls most of the resources and distributes them fairly among the people. State capitalism, on the other hand, is an economic system in which the state (the government) controls certain industries but allows private ownership and competition in others. Stalin's Russia and Mao's China were communist and socialist because they aimed to create a society with equality and fair distribution of resources. They also had state control over most of their economies. However, they were also state capitalist because the government controlled certain key industries like coal mining and steel production. Many people wrongly attribute deaths to communism as if it was the economic system that killed them, but in reality, it was the leaders who caused these deaths through policies like collectivization of agriculture or forced industrialization. These policies often led to famines and other tragedies, but they were not inherent to communism or socialism - they were the result of poor decision-making by authoritarian leaders. So next time you hear someone say that communism kills, remember that it's not the economic system itself, but how it is implemented that matters.",
        'This game comes for 99 cents. If you have ever wanted to be a ghost hunter, this app is just the right one for you. Any fan of the Ghostbusters franchise will immediately fall in love with this game. This game works in similar ways to Pokémon GO. You need to walk around with your the game on. You must be connected to the GPS for this is an augmented reality game. You will be to locate and see ghosts in the backdrop of the world as you see it using your phone’s camera. The AR mode works in such a way that it shows you the map when it is held in a parallel to the ground.',
        "People might not buy them because fixing a house takes time and money. They must save money for this project, and many people don't have enough savings or don't want to invest time and effort into the homes. Some may worry about safety or security issues after moving to a less developed area like Detroit. Also, if they buy a home in a nice neighborhood with good schools and shopping options, it can increase their quality of life more directly. But for people who do choose to fix these houses up, it could be very rewarding as they help improve a whole community and maybe even earn money when they sell the house later. It's just not an easy choice or one that everyone will make.",
        'In the article, they detail the four major trends happening in the workplace today as digital forces continue to play a bigger and bigger role in the way we do business. At NKD, we believe “Remarkable things happen when people feel valued, connected and empowered to make a difference”, and this belief is becoming truer and truer, bolder and bolder, stronger and stronger as we move into the digital-era of business. The organisations know that people are their most valuable asset! To succeed in the digital-era of work, businesses and organisations must invest in their people; they must show their people that although machines are getting smarter and ways of working are getting more agile, the power of people is still the greatest asset to the business.',
        'In November 1705, another architectural achievement occurred with the completion of the Royal Observatory at Greenwich, also designed by Sir Christopher Wren. This building not only marked a significant advancement in astronomical observations but also had architectural significance as it was built to resemble the ancient Greek temples. In comparison to these two projects, the construction of Blenheim Palace and the remodeling of the Jesuit Church in Vienna were relatively minor in scope and architectural innovation compared to the projects completed in London during this time period. Blenheim Palace was built between 1705 and 1724, while the remodeling of the Jesuit Church in Vienna occurred sometime during that same period. While both projects were significant for their repective regions, they did not have the architectural impact or innovation that the projects completed in London did during this time period.',
        "Yasser Arafat, the Chairman of the Palestine Liberation Organization (PLO), did give a speech at the United Nations General Assembly (UNGA) in Geneva on September 30, 1974. This was due to the United States denying him a visa to visit New York and attend the UNGA session there. The UNGA sessions in New York and Geneva run concurrently, so Arafat's speech at the Geneva session was an alternative for him to address the international community.",
        'All the plants enjoy the heat and humidity of the summer on the porch. Our outdoor oval gardens come into Self-sown larkspur plants provide height, and the ageratum and alysum begin to fill in along the edge. If you click on the picture, you will see a few orange strawflowers. Overall, these did not do well, but some developing statice will add to our dried-flower collection. This is a close-up of one orchid speciman.',
        'But if your site is substantial and difficult in addition to obtains plenty of guests, shared hosting may perhaps prevent your own increase and progression. This can be a good plan to get a specific web host. Have a look at back up owners should you not such as distinct tasks of your current hosting company. In case your webhost ends up definitely not being everything you estimated, you can certainly move to help one of many solutions you’ve researched and will not ought to risk your web site getting straight down entirely because you determine a fresh approach. Be careful any time considering internet hosting bundles declaring infinite services. In particular, if you’re made available unlimited disk living space, there may be constraints on what record varieties tend to be authorized. Examine the particular website hosts you’re taking a look at with regard to money-back ensures. When you become unhappy with all the services inside calendar month regarding registering, you ought to have the possibility to be to cancel and be given a reimbursement.',
        'View detailed maps of General Plan and Zoning designations. Browse area maps of City Council Districts, Priority Development Areas, and more. Browse demographics information from Census 2010 and the latest City population figures. Review maeps and data related to past and future City development. Access special purpose maps of historic resources, neighborhoods, smart growth, and more.',
        'Reviews Most recent Top reduced appetite and cravings (2). Pages with related products. In the skin of the famous by Oprah Winfrey. The higher the HCA(hydroxycitric acid) levels of the neurotransmitter serotonin. The absolute most important thing Secret Nutrition was eh, average, but again, if you have. This generally causes people to from the Garcinia Cambogia fruit the link shown on the. This shopping feature will continue to load items.',
        "The Boeing B-17, and the Consolidated B-24 were the United States' two standard heavy bombers until the introduction of the B-29 Superfortress. B-17s were flown by the United States Army Air Corps (USAAC), throughout the American participation in the Second World War. They were used by the US Eighth Air Force, based in thne UK, to bombard German targets in Europe during daylight hours, a method which resulted initially in very heavy losses of aircraft and crew. As B-17 refinements progressed, along with better pilot training and tactics, it would become a formidable adversary in the Allied war against Germany.",
        'It is called origin and it is automatically created when you cloned your project from dropbox. Now you are done with all the changes and these are now synchronized on all your developer machines. Getting the changes for your project on a machine that already has your project. I hope that you will find this method useful fow synchronizing code between your computer via dropbox and git.',
        "This means that Europe is actually moving away from Asia over time. The earth's crust is made up of large pieces called plates, which can move around on top of a softer layer in the earth called the mantle. When two plates rub against each other, it causes earthquakes and volcanoes. Europe used to be part of the same plate as Asia, but millions of years ago, their plates began to separate.",
        'These applications underline the need for truly multidisciplinary approaches to risk assessment, where risk-reducing behavior can be modeled and the implications on risk levels assessed. This point was recently highlighted by the UK Climate Change Risk Assessment, which is explicitly designed to inform public policy and identify those areas where adaptation action is deemed most important (Adaptation Sub-Committee, 2016). Understanding the interactions between risk reduction behavior and how vulnerability and exposure can change over time is an important component of assessing risks and designing response mechanisms (Di Baldassarre et al., 2015; Dawson, Peppe, & Wang, 2011). In conclusion, scientific evidence shows that the only truly sustainable response to flooding and climate change is a significant increase in efforts to reduce the underlying risks and influence risk drivers.',
        "He started his career as a Member of Parliament from the National List of the Sri Lanka Freedom Party (SLFP) in 2001 and later joined the United People's Freedom Alliance (UPFA). Amarasinghe is known for advocating on behalf of tqe common people, often focusing on their welfare. In addition to politics, he has also been a notable member of the Sri Lankan cricket team as an opening batsman and wicket-keeper in the 1980s and 1990s. As a parliamentarian, Amarasinghe has held various posts including Minister of Ports and Aviation (2004), Minister of Irrigation (2006), Deputy Minister of Health (2015-2017), and currently he is the Deputy Speaker of Parliament. His life can be seen as primarily focused on public service through both cricket and politics in Sri Lanka.",
        "* Stagnation stage: In this phase, the couple's communication becomes negative, repetitive, and unproductive. They may feel disconnected or emotionally distant from each other. Examples of topics during this stage include resentment, contempt, defensiveness, stonewalling, criticism, and emotional cutoff. * Resurrection stage: During this phase, the couple begins to work on rebuilding their relationship by addressing and resolving conflicts that led to stagnation. They learn new communication skills and strategies for improving their interactions. Examples of topics during this stage include conflict resolution, active listening, assertiveness, empathy, and respect. * Termination stage: In this phase, the couple has successfully rebuilt their relationship, and they feel closer, more connected, and happier together. They have developed healthy communication patterns and are able to resolve conflicts effectively.",
        'The expression should be written as a single fraction first before performing the division. So, we have:\n\n$\\frac{10}{2} \\div \\frac{1}{4} = \\frac{10}{2} \\times \\frac{4}{1} \\div \\frac{1}{1} \\times \\frac{4}{1}$\n\nNow, we can perform multiplication and division from the inside of the parentheses first, then the division outside:\n\n$\\frac{10\\times 4}{2\\times 1\\times 1}$\n\nThis simplifies to:\n\n$\\frac{40}{2}$\n\nNow, divide by 2:\n\n$20$\n\nSo, $\\boxed{20}$ is the answer.',
        "I do not have access to real-time information or current events, and am unable to provide any information regarding Don Olsen's upcoming visit or casting announcements. For the most up-to-date information, please check reputable entertainment news sources or the official Don Olsen website.",
        'The Circumstances:\n\n* Weston, along with a group of traders and soldiers, were traveling through the territory of the Menominee tribe. * Despite prior negotiations, tensions arose, and the Native Americans attacked the group. * Weston was killed in the battle, alongside 10 soldiers and several traders.',
        'This made each poppy unique and personal. This became really stressful & so I only made a few the following year as seen in the photo above. This year I haven’t made any due to changing my day job at the same time as I would of started making the poppies. I hope people who still have their poppies will still make a contribution to the appeal. We are 11 days into 2016 and I have noticed on media people associating a word to 2016. It’s not all about setting new year resolutions but having a more meaningful year.',
        'Yes oh! Upon all the Nigerian designers, no one could hook them up for the occasion??? Seriously, … wtf? Seriously, I think Sasha looks good! I just love her self confidence, she carries off whatever she wears very well. I sincerely agree with ya. Sasha has a lot of self-confidence, carries herself well, reps Nigeria well in her style of singing, performing and the whole works or nine yards. I guess some naija female performers could learn from her….seriously.',
        "Berman-Yurin's decision to leave Latvia without permission from the Communist Party and join the German Communist Party was seen as a betrayal by the Soviet Union, which viewed any form of opposition or dissent as treasonous. As a result, Berman-Yurin was expelled from the Soviet Union as a deserter. This decision had significant implications for his involvement in the trial of the sixteen, as it called into question his loyalty to the Communist cause and undermined the credibility of their arguments. Berman-Yurin's decision to leave Latvia without permission from the Communist Party was seen as a major breach of discipline and a violation of party rules. It demonstrated that he was willing to defy authority and challenge the established order, which went against everything the Soviet Union stood for.",
        'Your gift helps rescue a Rohingya family from this new crisis. Over 700,000 refugees - mostly women and children - have fled to Bangladesh to escape horrific violence in Myanmar. Rohingya families are living in unsafe camps, and now what little they have is at risk of being washed away. It only costs $11 to deliver urgently needed aid, including fortified shelter materials, to a family struggling to survive this crisis. And, because of special matching grants, your gift will TRIPLE to help three families! Rohingya refugees are some of the most vulnerable and marginalized people in the world. Your urgent gift today not only provides life-saving aid but lets them know and experience God’s powerful love. Give now to rescue a refugee family in crisis.',
        'The new arrangement incorporated elements of multiple genres and rhythms, which not only made it more interesting for listeners but also opened up possibilities for remixes and live performances. 3. Appealing to arious demographics: This re-imagined version of "Marry Me" resonated with different age groups and music tastes. The inclusion of rap artists like Snoop Dogg and Lil Wayne appealed to younger audiences, while the original rock roots of the song maintained its appeal to the fans who enjoyed traditional pop rock. This wide audience reach was key in making it a successful crossover hit. 4. Creating a relatable narrative: The song\'s theme of love and commitment resonated with listeners who could identify and relate to the emotions expressed in the lyrics. This emotional connection made "Marry Me" more memorable, leading to increased fan engagement and loyalty towards the song. 5.',
        'On February 23, 2014, Editor of walls-interiors.com published Stylish false ceiling with light for modern living room with brown sofa sets picture as your inspiration. If you want to see the picture in full size, just right click on the picture above and then select "Open Link in New Tab" in your favorite browser. You can also download this Stylish false ceiling with light for modern living room with brown sofa sets picture by clicking the picture caption which is located under the picture and then save on your device. We also featured related photographic to the Stylish false ceiling with light for modern living room with brown sofa sets as thumbnail below, so you can easily access them as what you want. We hope you enjoy being here and feel free to contact our team at the contact page when you need any help or another such as, we will be happy to assist you.',
        "3. The Dawson Highway: This is a major road that passes through Simmie, connecting Bundaberg and Gladstone. It provides easy access to nearby towns and cities. 4. The Fitzroy River: While not within Simmie itself, the Fitzroy River is an important river system located to the northwest of Simmie. It flows into the ocean near Gladstone and is an essential part of the region's ecosystem. 5. Nielson Park: This is a popular park situated on the banks of the Burnett River, offering picnic areas, walking trails, and opportunities for swimming and boating. Overall, Simmie is surrounded by natural beauty that includes rivers, mountains, and scenic landscapes that contribute to its rural charm.",
        'Contact us anytime for a quick quote on your packaging requirements. You can view our extensive range of packaging products and supplies in our 2017 packaging brochure, downloadable as a PDF bjelow. Our packaging products & consumables range is very extensive and varied; We can cover all packaging requirements & we provide a quick turnaround on all orders.',
        'The brand new collacation could be remarkable. With marketing/advertising, you may use mulberrys to design graphics that will go on billboards, commercials, and flyers. Helping landowners understand ways they can reduce their influence on the Cape Neddick watershed and educating pet owners about the effect of pet waste are vital education goals. ofreciA? entonces de forma gratuita el nombre e imagen de su perro para denominar a los premios. com Pingback: computere second hand Pingback: just click for source Pingback: login. This web site gives good quality YouTube videos; I always download the dance contest show videos from this site. If you are to watch funny videos online then I suggest you to go to see this website, it consists of truly so funny not only videos but also other information.',
        'They are relatively inexpensive, and moldings will add a touch of elegance to interior rooms. Henderson Custom Painting painters are skilled in providing light carpentry services, including installing many styles of trim and moldings to create elegant accents to your interior rooms. Add class to your dining room with moldings or chair rails. Installation of wainscoting in kitchens, restrooms and other areas is also a popular carpentry service in Foxcroft. Henderson Custom Painting carefully prepares all interior surfaces for trim by sanding, priming and painting as required. Let Henderson Custom Painting freshen up your Foxcroft home with light caqpentry accents. The trusted painters of Foxcroft can make your home even more spectacular with light carpentry services! Are you tired of looking at dented baseboards and door jams? Is the paint peeling or chipped? Sometimes a fresh coat of paint is enough to freshen up a room.']
    result = head_tail_api_pred_human(list_text, urls)
    print(result)

    labels = [True, True, False, False, True, True, True, True, False, False, True, False, True, False, False, False,
              False, True, True, True, True, True, False, True, False, True, True, False, False, False, False, False,
              False, True, False, True, True, True, True, True, False, False, True, False, True, False, True, False,
              False, False]
    result1 = [not l for l in labels]
    print(result1)
    count = 0
