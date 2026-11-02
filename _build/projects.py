"""Project content, carried over from the old hands4unity.org site.

Each project keeps its old URL slug so existing links keep working.
Image paths are relative to assets/img/.
Body text is HTML.

Programmes that are running now have "running": True. The homepage lists them under
"How we can help" with their "summary" facts and "action" button, so set or remove the flag
when a programme starts or ends.
"""

PROJECTS = [
    {
        "slug": "kids-can-code-summer-camp-2025",
        "title": "Kids Can Code 2025 Camp",
        "kind": "Programme",
        "when": "August 2025",
        "where": "Barbican Centre, Drogheda",
        "excerpt": "A hands-on summer coding camp for children aged 7 to 12, full of games, storytelling and creative challenges.",
        "cover": "projects/kids-can-code/cover.png",
        "card": "projects/kids-can-code/kids-laptop.jpg",
        "sections": [
            {
                "heading": "Empowering young minds through creativity, curiosity and code",
                "image": "projects/kids-can-code/kids-laptop.jpg",
                "body": """
<p>This summer, Hands4Unity was proud to run Kids Can Code again: an exciting, hands-on coding camp designed for children aged 7 to 12. Over the course of the programme, young participants explore the world of technology in a fun and supportive environment.</p>
<p>Through games, storytelling and interactive challenges, children:</p>
<ul class="ticks">
<li>Learn the fundamentals of coding using Scratch and block-based languages.</li>
<li>Develop problem-solving and critical thinking skills.</li>
<li>Build their own simple animations, games and digital stories.</li>
<li>Work on mini-projects they can proudly showcase at the end.</li>
</ul>
<p>We believe every child can code when given the right tools, guidance and encouragement. No prior experience is needed, just curiosity and imagination.</p>
""",
            },
            {
                "heading": "A safe, fun and enriching summer",
                "image": "projects/kids-can-code/coding-class.jpg",
                "body": """
<p>At Hands 4 Unity, we know how important it is for your child to have a safe, fun and enriching environment during the summer.</p>
<p>By taking part in Kids Can Code, children gain valuable digital skills, make new friends and develop confidence in a fast-changing world. No prior experience is required, just a willingness to learn and explore.</p>
""",
            },
        ],
        "details_title": "2025 camp details",
        "details": [
            ("calendar", "Dates", "11, 12, 13 and 14 August 2025"),
            ("clock", "Time", "10:00am to 1:00pm"),
            ("pin", "Location", "Barbican Centre, Drogheda"),
            ("user", "Ages", "7 to 12"),
            ("euro", "Cost", "€60"),
        ],
        "cta": {
            "title": "Interested in the next camp?",
            "text": "Get in touch and we will let you know when bookings open for the next Kids Can Code camp.",
            "label": "Register your interest",
            "href": "contact-us/",
        },
    },
    {
        "slug": "taste-of-all-nations-2025",
        "title": "Taste of All Nations 2025",
        "kind": "Event",
        "when": "June 2025",
        "where": "Ardee, Co. Louth",
        "excerpt": "On a rainy day filled with rhythm, colour and connection, Taste of All Nations brought the town of Ardee to life.",
        "cover": "projects/toan-2025/cover.jpg",
        "card": "projects/toan-2025/cover.jpg",
        "sections": [
            {
                "heading": "A celebration of culture, unity and shared joy in Ardee",
                "image": "projects/toan-2025/cover.jpg",
                "body": """
<p>On a rainy day filled with rhythm, colour and connection, Taste of All Nations 2025 brought the town of Ardee to life in the most vibrant way possible.</p>
<p>Organised by Hands4Unity, sponsored by Louth County Council and the local community, Louth Local Development, Healthy Ireland and Louth Volunteer Centre, and supported by an incredible team of volunteers, the event offered a unique experience where cultures from all around the world met through food, music, dance and human connection. From the smell of rich spices to the sounds of traditional drums and modern beats, every corner of the event told a story of people, pride and togetherness.</p>
<p>Crowds gathered to taste dishes from dozens of countries, try traditional dance steps, admire colourful attire and listen to powerful performances that blended heritage and modern creativity. It was a feast for all the senses and, above all, for the soul.</p>
""",
            },
            {
                "heading": "More than a celebration: a statement of unity",
                "image": "projects/toan-2025/dancers.jpg",
                "body": """
<p>Taste of All Nations is more than a cultural showcase. It is a living example of what happens when communities come together in respect, curiosity and joy. It reflects Hands4Unity's mission to build bridges between people of different backgrounds, encouraging understanding and connection in every interaction.</p>
<p>In a world that often highlights differences, this event reminded us of everything we have in common, and how beautiful those differences really are when we share them openly.</p>
""",
            },
            {
                "heading": "Thank you to our supporters",
                "image": "projects/toan-2025/volunteers.jpg",
                "body": """
<p>We are deeply grateful to every individual and organisation who helped make this event possible. Without our funders, community leaders, performers, cooks, hosts and tireless volunteers, Taste of All Nations simply could not have happened.</p>
<p>Your time, your resources and your heart made all the difference.</p>
""",
            },
        ],
    },
    {
        "slug": "coaching-and-mentoring-for-job-seekers",
        "title": "Coaching and Mentoring for Job Seekers",
        "kind": "Programme",
        "when": "Ongoing",
        "where": "Drogheda",
        "excerpt": "Free, practical support for migrant and Irish women who want to enter the workforce, return to work or change career.",
        "running": True,
        "summary": [("When", "By appointment"), ("Where", "Drogheda"), ("Cost", "Free")],
        "action": ("Book a free session", "contact-us/?subject=Coaching%20appointment"),
        "cover": "projects/coaching/cover.jpg",
        "card": "projects/coaching/cover.jpg",
        "sections": [
            {
                "heading": "Looking for a job in Ireland and not sure where to start?",
                "image": "projects/coaching/cover.jpg",
                "body": """
<p>You don't have to do it alone. At Hands4Unity, we support migrant and Irish women who want to enter the workforce, return to employment or change careers, with real, practical guidance every step of the way.</p>
<p>Our employment-focused support programme offers:</p>
<ul class="ticks">
<li><strong>One-to-one coaching</strong> to define your goals and build your confidence.</li>
<li><strong>CV clinics</strong> to help you create or improve your CV.</li>
<li><strong>Interview preparation</strong> with real Irish context and feedback.</li>
<li><strong>Mentorship</strong> from professionals who know the Irish job market.</li>
<li><strong>Navigation support</strong> to help you understand how recruitment works here.</li>
</ul>
<p>Whether you've never worked in Ireland, or you're just feeling stuck or overlooked, we'll help you unlock your potential and take the next step toward your career goals.</p>
""",
            },
            {
                "heading": "Who is it for?",
                "image": "projects/coaching/who-is-it-for.jpg",
                "body": """
<p>This programme is open to anyone currently looking for work, whether you're actively applying, considering a return to employment, or simply want to better understand the Irish job market. We especially welcome:</p>
<ul class="ticks">
<li>Migrant and refugee job seekers, including those still building their English or adjusting to a new work culture.</li>
<li>Irish job seekers facing barriers such as long-term unemployment, lack of qualifications or low confidence.</li>
<li>Women returning to work after maternity leave, caregiving or a career break.</li>
<li>Young adults and recent graduates looking for guidance in entering the workforce.</li>
<li>People changing careers or reorienting after redundancy or life changes.</li>
</ul>
<p>Whether you have no experience or many years behind you, you are welcome here. Our approach is inclusive, human-centred and practical, with a strong focus on helping you take clear, confident steps forward.</p>
""",
            },
            {
                "heading": "Book a free appointment",
                "image": "projects/coaching/book-free-session.png",
                "body": """
<p>No matter where you're starting from, your journey matters, and we're here to support it. Whether you need help polishing your CV, preparing for interviews or figuring out where to begin, our team is ready to guide you.</p>
<p>Book a free one-to-one appointment and take the first step toward your future with confidence. Together, we'll work on what you need, at your pace, in a safe and supportive environment.</p>
<p><strong>Places are limited, so don't wait too long.</strong></p>
""",
            },
        ],
        "cta": {
            "title": "Book your free session",
            "text": "Send us a message or call us on 087 003 0568 to make your appointment.",
            "label": "Book an appointment",
            "href": "contact-us/?subject=Coaching%20appointment",
            "secondary": ("Call 087 003 0568", "tel:+353870030568"),
        },
    },
    {
        "slug": "tuesdays-sewing-workshop-in-english",
        "title": "Tuesday's Sewing Workshop in English",
        "kind": "Programme",
        "when": "Every Tuesday",
        "where": "Barbican Centre, Drogheda",
        "excerpt": "Improve your English and learn a practical skill in a warm, welcoming space. Every Tuesday evening in Drogheda.",
        "running": True,
        "summary": [("When", "Every Tuesday, 6:00pm to 7:30pm"), ("Where", "Barbican Centre, Drogheda"), ("Cost", "€5 per person")],
        "action": ("Join a workshop", "contact-us/?subject=Sewing%20Workshop"),
        "cover": "projects/sewing/cover.jpg",
        "card": "projects/sewing/cover.jpg",
        "sections": [
            {
                "heading": "Learn, create and connect in Drogheda",
                "image": "projects/sewing/cover.jpg",
                "body": """
<p>Looking to improve your English and learn a practical skill in a warm, welcoming space? The Sewing Workshop in English is a unique programme that combines language learning with creativity, designed especially for non-native English speakers in the Drogheda area.</p>
<p>Through hands-on, beginner-friendly sewing sessions, participants develop their English in real-life, everyday situations while also learning to sew. It's more than a class: it's a space to grow in confidence, build friendships and discover new opportunities.</p>
""",
            },
            {
                "heading": "Better English, and sewing techniques",
                "image": "projects/sewing/materials.jpg",
                "body": """
<p>What you'll gain:</p>
<ul class="ticks">
<li><strong>Better English</strong> through interactive, practical learning.</li>
<li><strong>Sewing techniques</strong> for personal use or future employment.</li>
<li><strong>Social connection</strong> and a stronger sense of community.</li>
</ul>
<p>Whether you're new to sewing or new to English, this workshop is for you.</p>
""",
            },
            {
                "heading": "Ready to get involved?",
                "image": "projects/sewing/collage.png",
                "body": """
<p>We're open and excited to welcome new participants. No previous sewing experience or perfect English is needed, just curiosity and a willingness to try. Come as you are, and let's learn and grow together.</p>
<p>We also welcome volunteers, sewing tutors, language mentors and anyone who believes in empowering communities through skills and connection. Whether you want to share your time, donate materials or simply spread the word, there's a place for you.</p>
""",
            },
        ],
        "details_title": "Workshop details",
        "details": [
            ("calendar", "When", "Every Tuesday"),
            ("clock", "Time", "6:00pm to 7:30pm"),
            ("pin", "Location", "The Barbican Centre, William St, Drogheda, Co. Louth"),
            ("euro", "Cost", "€5 per person"),
        ],
        "cta": {
            "title": "Join the workshop or volunteer",
            "text": "Want to take part, teach or donate materials? We'd love to hear from you.",
            "label": "Get in touch",
            "href": "contact-us/?subject=Sewing%20Workshop",
        },
    },
    {
        "slug": "africa-day-2025",
        "title": "Africa Day 2025",
        "kind": "Event",
        "when": "24 May 2025",
        "where": "Drogheda",
        "excerpt": "Drogheda came alive with the sounds, colours and rhythms of the African continent as Hands4Unity co-hosted Africa Day.",
        "cover": "projects/africa-day-2025/cover.jpg",
        "card": "projects/africa-day-2025/cover.jpg",
        "sections": [
            {
                "heading": "A celebration of heritage and unity",
                "image": "projects/africa-day-2025/portrait-trio.jpg",
                "body": """
<p>On 24 May, Drogheda came alive with the sounds, colours and rhythms of the African continent as Hands4Unity proudly co-hosted Africa Day 2025: a heartfelt celebration of culture, identity and unity.</p>
<p>The event brought together people from diverse backgrounds to honour the contributions of African communities to Irish life. Traditional dances lit up the stage, the aroma of homemade dishes filled the air, and colourful attire turned every moment into a celebration of pride and connection. More than a cultural event, Africa Day 2025 became a space of shared humanity, where stories were exchanged, friendships sparked and cultural bridges strengthened.</p>
""",
            },
            {
                "heading": "Diversity is a strength",
                "image": "projects/africa-day-2025/gallery-01.jpg",
                "body": """
<p>At its core, Africa Day reflects a simple truth: diversity is a strength. This year's celebration showed how deep the desire is within our communities to connect across cultures. In a world where divisions can dominate the headlines, this event reminded everyone of the beauty in coming together.</p>
<p>Africa Day can grow into a county-wide celebration that welcomes everyone. We believe future editions in Drogheda should be built in partnership with local authorities, so the event can reflect the full richness of our multicultural community. Hands4Unity is ready to continue its role as organiser and connector.</p>
<p>To everyone who attended, performed, volunteered or simply showed up with curiosity and an open heart: thank you. Your presence made the day unforgettable.</p>
""",
            },
        ],
        "gallery": [f"projects/africa-day-2025/gallery-{i:02d}.jpg" for i in range(2, 14)],
    },
    {
        "slug": "taste-of-all-nations-2024",
        "title": "Taste of All Nations 2024",
        "kind": "Event",
        "when": "2024",
        "where": "Drogheda",
        "excerpt": "Our community integration festival returned, bringing food, music and dance from around the world to Drogheda.",
        "cover": "projects/toan-2024/cover.jpg",
        "card": "projects/toan-2024/cover.jpg",
        # The old site had photos but no write-up for this event.
        "sections": [
            {
                "heading": "Taste of All Nations 2024",
                "image": "projects/toan-2024/brazil-stall.jpg",
                "body": """
<p>Taste of All Nations returned in 2024, bringing together food stalls, performers and families from the many cultures that make up our community.</p>
""",
            },
        ],
    },
    {
        "slug": "international-womens-day-2024-2",
        "title": "International Women's Day 2024",
        "kind": "Event",
        "when": "March 2024",
        "where": "Drogheda",
        "excerpt": "Celebrating the women of our community on International Women's Day.",
        "cover": "projects/iwd-2024/cover.jpg",
        "card": "projects/iwd-2024/cover.jpg",
        # The old site had a photo but no write-up for this event.
        "sections": [
            {
                "heading": "Celebrating International Women's Day",
                "image": "projects/iwd-2024/cover.jpg",
                "body": """
<p>Hands 4 Unity marked International Women's Day 2024 by celebrating the women of our community and the cultures they bring to it.</p>
""",
            },
        ],
    },
    {
        "slug": "food-festival-lifestyle-development",
        "title": "Food Festival with Lifestyle Development",
        "kind": "Event",
        "when": "Christmas market",
        "where": "Co. Louth",
        "excerpt": "A Christmas market and food festival run jointly with Lifestyle Development.",
        "cover": "projects/food-festival/cover.jpg",
        "card": "projects/food-festival/cover.jpg",
        "sections": [
            {
                "heading": "Christmas market: a joint project",
                "image": "projects/food-festival/cover.jpg",
                "body": """
<p>A Christmas market and food festival run as a joint project between Hands 4 Unity and <a href="https://lifedev.ie/" target="_blank" rel="noopener">Lifestyle Development</a>.</p>
""",
            },
        ],
    },
    {
        "slug": "hse-christmas-party",
        "title": "HSE Christmas Party 2023",
        "kind": "Event",
        "when": "Christmas 2023",
        "where": "Drogheda",
        "excerpt": "Supporting the Indian community in Drogheda at their annual Christmas party.",
        "cover": "projects/christmas-2023/party.jpg",
        "card": "projects/christmas-2023/party.jpg",
        "sections": [
            {
                "heading": "Indian community annual Christmas party",
                "image": "projects/christmas-2023/party.jpg",
                "body": """
<p>Hands 4 Unity was delighted to support the Indian community in Drogheda at their annual Christmas party.</p>
""",
            },
        ],
        "gallery": ["projects/christmas-2023/cover.jpg"],
    },
    {
        "slug": "inaugural-taste-of-all-nations",
        "title": "Inaugural Taste of All Nations 2019",
        "kind": "Event",
        "when": "23 November 2019",
        "where": "Drogheda",
        "excerpt": "Our first community integration festival: a vibrant showcase of international cuisine, music, dance and activities.",
        "cover": "projects/toan-2019/toan-3.jpg",
        "card": "projects/toan-2019/toan-3.jpg",
        "sections": [
            {
                "heading": "Our inaugural community integration festival",
                "image": "projects/toan-2019/toan-5.jpg",
                "body": """
<p>Taste of All Nations celebrates cultural diversity through a vibrant showcase of international cuisine, music, dance and activities. It brings together people from all walks of life, fostering unity and understanding within our community, with delicious food from around the world, engaging performances and family-friendly fun all in one place.</p>
<p>The event was opened by the Deputy Mayor of Drogheda, Cllr Michelle Hall. Our esteemed guest Fergus O'Dowd TD attended with his wife, and Gráinne Berrill of Louth Volunteer Centre organised a team of volunteers who helped out on the day.</p>
""",
            },
            {
                "heading": "Thank you to our performers and supporters",
                "image": "projects/toan-2019/toan-1.jpg",
                "body": """
<p>Special thanks to everyone who made the event a huge success, especially the performers: Mudra School of Classical Indian Dance, Lo Lo School of Irish Dancing, and the Philippine dance performance put together by the nursing staff of Our Lady of Lourdes Hospital.</p>
<p>A total of <strong>€500</strong> was raised from raffle sales on the day. It was all donated to Drogheda Care for Older People to help buy security alarms for the people they support.</p>
<p>The event was proudly supported by EBS Drogheda, Scholars Inn Hotel, Cement Factory, Drogheda Lions Club and Drogheda Credit Union, and was covered by the Drogheda Independent and Drogheda Leader.</p>
""",
            },
        ],
        "gallery": ["projects/toan-2019/toan-2.jpg", "projects/toan-2019/toan-4.jpg", "projects/toan-2019/toan-3.jpg"],
    },
    {
        "slug": "feile-an-paisti",
        "title": "Féile an Páistí",
        "kind": "Event",
        "when": "7 September 2019",
        "where": "Navan, Co. Meath",
        "excerpt": "Supporting the Navan community at their Féile an Páistí, a festival for children from disadvantaged areas.",
        "cover": "projects/feile-an-paisti/cover.jpg",
        "card": "projects/feile-an-paisti/cover.jpg",
        "sections": [
            {
                "heading": "A festival for the children of Commons Road",
                "image": "projects/feile-an-paisti/festival.jpg",
                "body": """
<p>Hands 4 Unity supported the Navan community at their Féile an Páistí festival on 7 September 2019. This small festival is held for children from disadvantaged areas around Commons Road in Navan.</p>
""",
            },
        ],
        "gallery": ["projects/feile-an-paisti/cover.jpg"],
    },
]

BY_SLUG = {p["slug"]: p for p in PROJECTS}
