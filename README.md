# 🧠 LLM-Twins: Simulating Human Responses to Political Bias Using Generative Agents

Welcome to the companion code repository for the master's thesis:  
**“LLM-Twins: How Extremist SOSEC-based Generative Agents React to Bias in News”**  
by Miriam Coccia, University of Trier (2025).

This project explores whether Large Language Models (LLMs) can simulate human behavior when equipped with real sociodemographic and political data — and how such agents respond to politically biased news articles.

---

## 🧪 Research Goals

This project supports a two-phase experiment:

1. **Agent Modeling**  
   Generative agents ("LLM-Twins") are created using detailed persona prompts derived from U.S. participants in the SOSEC questionnaire who reported extreme political views.

2. **Bias Exposure**  
   These agents are exposed to real-world biased news articles (from Fox News and MSNBC) to measure:
   - Opinion shifts (polarization vs. mitigation)
   - Alignment with known human response patterns

---

## ❓ Research Questions

- **RQ1**: Can generative agents replicate individual-level responses from real participants when given only demographic and political context?  
- **RQ2**: Do these agents behave like humans when exposed to politically biased media?

---

## 🧠 Models Used

**Meta-Llama-3-70B-Instruct**  
Chosen for its strong alignment capabilities and instruction tuning, available via the University of Trier’s CL-Server infrastructure.

---

## 📊 Key Concepts

- **SOSEC Dataset**: Longitudinal survey on political sentiment across Germany and the U.S.  
- **Persona Prompting**: Rich individual-level metadata used to guide agent behavior.  
- **Reliability Framework**: Quantitative scoring system (MAE, MSE, accuracy metrics) to measure alignment between agents and humans.  
- **Media Bias Articles**: Articles from Fox News and MSNBC used to test susceptibility to opinion shifts.

---

## 📄 License

This repository is licensed under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).  
You must provide appropriate credit if you use this work.

---

## 🙋 Contact

Feel free to reach out with questions or collaborations:

- 📧 [LinkedIn: Miriam Coccia](https://www.linkedin.com/in/miriam-coccia-2a5998190/)
- 🧑‍💻 GitHub: [@miriamcoccia](https://github.com/miriamcoccia)
