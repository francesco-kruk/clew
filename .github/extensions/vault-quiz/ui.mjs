const form = document.querySelector("#quiz");
const button = document.querySelector("#submit");
const message = document.querySelector("#message");
let submitted = false;
let evidencePending = false;

function announce(text, error = false) {
    message.textContent = text;
    message.classList.toggle("error", error);
}

async function request(path, options) {
    const response = await fetch(path, options);
    const body = await response.json();
    if (!response.ok) {
        const error = new Error(body.error || `Request failed (${response.status}).`);
        error.quizSaved = body.quizSaved === true;
        throw error;
    }
    return body;
}

function render(state) {
    submitted = state.submitted;
    evidencePending = ["pending", "error"].includes(state.learnerModel.status);
    document.querySelector("#title").textContent = `Quiz: ${state.topic}`;
    document.querySelector("#source").textContent = `Source: ${state.source}`;
    const container = document.querySelector("#questions");
    container.replaceChildren();
    state.questions.forEach((question, index) => {
        const fieldset = document.createElement("fieldset");
        const legend = document.createElement("legend");
        legend.textContent = `${index + 1} of 3 - ${question.concept}`;
        const label = document.createElement("label");
        label.htmlFor = `answer-${index}`;
        label.textContent = question.prompt;
        const answer = document.createElement("textarea");
        answer.id = label.htmlFor;
        answer.name = `answer-${index}`;
        answer.required = true;
        answer.maxLength = 16000;
        answer.readOnly = state.submitted;
        answer.value = question.answer ?? "";
        fieldset.append(legend, label, answer);
        if (state.submitted) {
            const heading = document.createElement("h3");
            heading.textContent = "Suggested answer (not an automatic grade)";
            const suggestion = document.createElement("p");
            suggestion.className = "suggestion";
            suggestion.textContent = question.suggestedAnswer;
            fieldset.append(heading, suggestion);
        }
        container.append(fieldset);
    });
    button.disabled = submitted && !evidencePending;
    button.textContent = evidencePending ? "Retry learner-model recording" : submitted ? "Answers saved" : "Submit and save answers";
    if (!submitted) {
        announce("Ready. Nothing has been saved yet.");
    } else if (evidencePending) {
        announce(`Quiz answers saved to ${state.savedPath}\nLearner-model recording is incomplete. ${state.learnerModel.error ?? "Retry to append the submission evidence."}`, true);
    } else if (state.learnerModel.status === "recorded") {
        announce(`Saved to ${state.savedPath}\nUngraded supplied-work evidence recorded in ${state.learnerModel.ledgerPath}\nNo concept knowledge was changed.`);
    } else {
        announce(`Saved to ${state.savedPath}\nThis older attempt remains ungraded and was not added to the learner model.`);
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (submitted && !evidencePending) return;
    const answers = [...form.querySelectorAll("textarea")].map((field) => field.value);
    if (answers.some((answer) => !answer.trim())) {
        announce("Please answer all three questions before submitting.", true);
        return;
    }
    button.disabled = true;
    announce("Saving answers...");
    try {
        render(await request("./submit", {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-Quiz-Token": document.querySelector('meta[name="quiz-token"]').content },
            body: JSON.stringify({ answers }),
        }));
    } catch (error) {
        if (error.quizSaved) {
            submitted = true;
            evidencePending = true;
            form.querySelectorAll("textarea").forEach((field) => { field.readOnly = true; });
            button.textContent = "Retry learner-model recording";
        }
        announce(`Could not confirm the complete save: ${error.message}\nYour answers remain in the form. Retry with the same answers.`, true);
        button.disabled = false;
    }
});

window.addEventListener("beforeunload", (event) => {
    if (!submitted && [...form.querySelectorAll("textarea")].some((field) => field.value)) {
        event.preventDefault();
        event.returnValue = "";
    }
});

try {
    render(await request("./state"));
} catch (error) {
    announce(`Unable to load quiz: ${error.message}`, true);
}
