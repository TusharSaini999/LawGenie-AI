// @ts-nocheck
import TeamCard from "./TeamCard";
import shobhitPhoto from "../../assets/shobhit.jpg";
import tusharPhoto from "../../assets/tushar.jpeg";
import siddarthPhoto from "../../assets/siddarth.jpeg";
const teamData = [
  {
    id: 1,
    name: "Siddhant Kumar",
    role: "Co-Founder",
    image: siddarthPhoto,
    linkedin: "https://www.linkedin.com/in/siddharth-kumar-3855b231/",
    github: "https://github.com/sidk-dev"
  },
  {
    id: 2,
    name: "Tushar Sahni",
    role: "Founder",
    image: tusharPhoto,
    linkedin: "https://www.linkedin.com/in/tushar-saini-105865373/",
    github: "https://github.com/TusharSaini999"
  },
  {
    id: 3,
    name: "Shobhit Singh",
    role: "Co-Founder",
    image: shobhitPhoto,
    linkedin: "https://www.linkedin.com/in/shobhit115/",
    github: "https://github.com/shobhit115"
  }
];

const TeamSection = () => {
  return (
    <section className="py-24 bg-bg" id="team">
      <div className="max-w-7xl mx-auto px-6">

        {/* Section Header */}
        <div className="text-center mb-20">
          <h2 className="text-sm font-bold text-(--color-primary) uppercase tracking-[0.3em] mb-4">
            The Team
          </h2>
          <p className="text-4xl md:text-5xl font-black text-(--color-t-primary) mb-6">
            Meet the Minds Behind LawGenie
          </p>
          <div className="h-1 w-20 bg-(--color-primary) mx-auto rounded-full" />
        </div>

        {/* 3-Member Specific Layout */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {teamData.map((member) => (
            <TeamCard key={member.id} {...member} />
          ))}
        </div>

      </div>
    </section>
  );
};

export default TeamSection;