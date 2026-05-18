from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.storage import PlannerDB


SOURCE = "year8-biology-grade9-bank"
SUBJECT = "Biology"


def row(topic, difficulty, question, answer, marks, explanation=""):
    return {
        "subject": SUBJECT,
        "topic": topic,
        "difficulty_level": difficulty,
        "question": question,
        "answer": answer,
        "marks": marks,
        "source": SOURCE,
        "explanation": explanation,
    }


def build_cell_biology():
    return [
        row("Cell Biology", 3, "A student observes a cell with a cell wall, chloroplasts, and a large permanent vacuole. Identify the type of cell and give one reason why each of these structures is useful.", "It is a plant cell. The cell wall supports the cell, chloroplasts absorb light for photosynthesis, and the large vacuole helps keep the cell turgid.", 4),
        row("Cell Biology", 4, "Explain why sperm cells, nerve cells, and root hair cells are all described as specialised.", "They are specialised because each has adaptations for a specific function: sperm cells swim to reach the egg, nerve cells carry impulses, and root hair cells absorb water and mineral ions efficiently.", 4),
        row("Cell Biology", 4, "A cell is 0.08 mm long. Convert this length into micrometres.", "80 micrometres.", 2),
        row("Cell Biology", 5, "A student says, 'All cells with a nucleus are exactly the same.' Explain why this statement is incorrect.", "Cells with nuclei contain genetic material, but different cell types are specialised for different functions and can have different structures, sizes, and numbers of organelles.", 4),
        row("Cell Biology", 5, "Explain how the surface area to volume ratio affects the size of cells.", "As a cell gets larger, its volume increases faster than its surface area, so substances cannot enter and leave quickly enough. This limits cell size or means exchange surfaces are needed.", 4),
        row("Cell Biology", 4, "Why do red blood cells not have a nucleus, and how does this help them do their job?", "Not having a nucleus leaves more space for haemoglobin, so they can carry more oxygen.", 3),
    ]


def build_organisation():
    return [
        row("Organisation", 3, "Put these in order from simplest to most complex: organ, cell, organism, tissue, organ system.", "Cell, tissue, organ, organ system, organism.", 2),
        row("Organisation", 4, "Describe how the stomach is adapted for digestion.", "It has muscular walls to churn food, glands that release acid and enzymes, and a lining that protects it from its own acid.", 4),
        row("Organisation", 4, "Explain the job of enzymes in digestion and why they are needed.", "Enzymes are biological catalysts that speed up the breakdown of large insoluble food molecules into smaller soluble molecules that can be absorbed.", 4),
        row("Organisation", 5, "A patient has blocked coronary arteries. Explain how this can affect the heart and the rest of the body.", "Blocked coronary arteries reduce blood flow to the heart muscle, so it receives less oxygen and glucose for respiration. The heart may not pump effectively, so less oxygenated blood reaches the body.", 5),
        row("Organisation", 4, "Why is the small intestine well adapted for absorbing digested food?", "It has villi and microvilli for a large surface area, a good blood supply, and a thin lining for rapid absorption.", 4),
        row("Organisation", 5, "Compare the roles of the xylem and phloem in plants.", "Xylem transports water and mineral ions from roots to leaves and also supports the plant. Phloem transports dissolved sugars such as sucrose around the plant in both directions as needed.", 4),
    ]


def build_infection_and_response():
    return [
        row("Infection and Response", 3, "State the difference between a pathogen and a toxin.", "A pathogen is a microorganism that causes disease. A toxin is a poison released by some pathogens.", 2),
        row("Infection and Response", 4, "Explain why antibiotics are useful against bacterial infections but not viral infections.", "Antibiotics target structures or processes in bacteria, but viruses reproduce inside host cells and do not have the same cell structures, so antibiotics do not kill them.", 4),
        row("Infection and Response", 4, "Describe two ways the skin helps defend the body against pathogens.", "It acts as a physical barrier and it produces antimicrobial secretions. Credit clotting/scab formation if explained.", 3),
        row("Infection and Response", 5, "A doctor gives a vaccine to a patient. Explain how this can lead to immunity.", "The vaccine contains dead or inactive pathogen antigens, which stimulate white blood cells to produce antibodies and memory cells. On future exposure, the memory cells respond faster and produce more antibodies, so the pathogen is destroyed before symptoms develop.", 5),
        row("Infection and Response", 5, "Explain why using too many antibiotics can lead to antibiotic-resistant bacteria.", "Some bacteria have mutations that make them resistant. Antibiotic use kills non-resistant bacteria, leaving resistant ones to survive, reproduce, and pass on the resistance.", 4),
        row("Infection and Response", 4, "A student says washing hands only removes visible dirt. Explain why handwashing reduces disease spread.", "Handwashing removes or kills microorganisms on the skin, so there are fewer pathogens to transfer to food, surfaces, or other people.", 3),
    ]


def build_bioenergetics():
    return [
        row("Bioenergetics", 3, "Write the word equation for photosynthesis.", "Carbon dioxide + water -> glucose + oxygen.", 2),
        row("Bioenergetics", 4, "State three factors that can limit the rate of photosynthesis.", "Light intensity, carbon dioxide concentration, and temperature.", 3),
        row("Bioenergetics", 4, "Explain why a plant kept in the dark cannot photosynthesise.", "Photosynthesis needs light energy to drive the reaction, so without light the plant cannot make glucose by photosynthesis.", 3),
        row("Bioenergetics", 5, "Compare aerobic respiration with anaerobic respiration in humans.", "Aerobic respiration uses oxygen and releases more energy. Anaerobic respiration does not use oxygen, releases less energy, and produces lactic acid.", 4),
        row("Bioenergetics", 5, "Explain why an athlete breathes more deeply after intense exercise.", "During intense exercise some anaerobic respiration may occur, producing lactic acid. Extra oxygen is needed afterwards to remove lactic acid and return the body to normal.", 4),
        row("Bioenergetics", 4, "A student moves a lamp closer to a pondweed sample and the bubble count rises. Explain what this shows.", "It suggests the rate of photosynthesis increased because higher light intensity provided more energy for photosynthesis, so more oxygen was produced.", 4),
    ]


def build_homeostasis():
    return [
        row("Homeostasis and Response", 3, "What is homeostasis?", "The regulation of internal conditions to maintain optimum conditions for function.", 2),
        row("Homeostasis and Response", 4, "Explain how sweating helps control body temperature.", "Sweat evaporates from the skin. Evaporation transfers energy away from the body, cooling it down.", 3),
        row("Homeostasis and Response", 4, "Describe the roles of receptor, coordinator, and effector in a response to a stimulus.", "Receptors detect a stimulus, the coordinator processes information, and effectors produce the response.", 3),
        row("Homeostasis and Response", 5, "A person's blood glucose rises after a meal. Explain how the body returns it towards normal.", "The pancreas releases insulin, causing body cells to take in more glucose and the liver and muscles to store glucose as glycogen, so blood glucose falls towards normal.", 5),
        row("Homeostasis and Response", 5, "Explain one way diabetes can affect homeostasis if it is not controlled properly.", "If blood glucose stays too high, cells do not regulate glucose properly and this can damage organs and blood vessels over time.", 4),
        row("Homeostasis and Response", 4, "Why do pupils become smaller in bright light?", "Circular muscles in the iris contract so less light enters the eye, protecting the retina.", 3),
    ]


def build_inheritance():
    return [
        row("Inheritance Variation and Evolution", 3, "State the difference between inherited variation and environmental variation.", "Inherited variation is caused by genes from parents, while environmental variation is caused by surroundings or life experiences.", 2),
        row("Inheritance Variation and Evolution", 4, "Give one example of continuous variation and one example of discontinuous variation.", "Continuous variation: height or mass. Discontinuous variation: blood group or eye colour categories used in the course.", 2),
        row("Inheritance Variation and Evolution", 4, "Why can selective breeding lead to health problems in some animals?", "Selecting only a few parents can reduce genetic variation and increase the chance of inherited defects being passed on.", 4),
        row("Inheritance Variation and Evolution", 5, "Explain how natural selection can cause a population to change over time.", "Variation exists in a population. Individuals with advantageous characteristics are more likely to survive and reproduce, passing on those alleles. Over many generations the advantageous alleles become more common.", 5),
        row("Inheritance Variation and Evolution", 5, "A new disease kills many members of a species, but a few survive. Explain how this could change the species over generations.", "The survivors may have alleles that give resistance. They reproduce and pass on these alleles, so the proportion of resistant individuals increases over generations.", 4),
        row("Inheritance Variation and Evolution", 4, "Explain why extinction is more likely when the environment changes very quickly.", "Species may not have enough time to adapt by natural selection, so they may fail to survive and reproduce.", 3),
    ]


def build_ecology():
    return [
        row("Ecology", 3, "Define a community in ecology.", "All the populations of different species living in a habitat.", 2),
        row("Ecology", 4, "Explain why energy is lost between trophic levels in a food chain.", "Energy is lost in waste materials, movement, and keeping warm, so not all biomass is transferred to the next level.", 4),
        row("Ecology", 4, "Why are decomposers important in ecosystems?", "They break down dead material and waste, releasing mineral ions back into the environment.", 3),
        row("Ecology", 5, "A scientist finds fewer top predators than producers in an ecosystem. Explain why this is expected.", "Biomass and energy decrease at each trophic level because some energy is lost at every stage, so fewer organisms can be supported at higher levels.", 4),
        row("Ecology", 5, "Explain how deforestation can reduce biodiversity.", "Removing trees destroys habitats and food sources, breaks food webs, and changes environmental conditions, so fewer species can survive.", 4),
        row("Ecology", 4, "Why is quadrat sampling repeated several times across a habitat?", "Repeating samples makes the data more reliable and helps account for uneven distribution of organisms.", 3),
    ]


def build_questions():
    rows = []
    rows.extend(build_cell_biology())
    rows.extend(build_organisation())
    rows.extend(build_infection_and_response())
    rows.extend(build_bioenergetics())
    rows.extend(build_homeostasis())
    rows.extend(build_inheritance())
    rows.extend(build_ecology())
    return rows


def main():
    db = PlannerDB()
    rows = build_questions()
    count = db.bulk_upsert_questions(rows)
    print(f"Imported {count} Biology grade-9-style questions into the SQLite question bank.")


if __name__ == "__main__":
    main()
