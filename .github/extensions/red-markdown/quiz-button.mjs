const button = document.querySelector("#quiz-button");
const status = document.querySelector("#quiz-status");

button.addEventListener("click", async () => {
    if (button.disabled) return;
    button.disabled = true;
    button.setAttribute("aria-busy", "true");
    status.hidden = false;
    status.textContent = "Requesting a quiz...";
    status.classList.remove("error");
    try {
        const response = await fetch("./quiz", {
            method: "POST",
            headers: { "X-Quiz-Token": document.querySelector('meta[name="quiz-token"]').content },
        });
        const body = await response.json();
        if (!response.ok) throw new Error(body.error || `Request failed (${response.status}).`);
        if (body.status !== "requested") throw new Error("The quiz request was not acknowledged.");
        status.textContent = "Quiz requested. Copilot will open it in a new canvas. Refresh this reader to request another.";
        button.title = "Quiz requested";
    } catch (error) {
        status.textContent = `Could not request a quiz: ${error.message}`;
        status.classList.add("error");
        button.disabled = false;
        if (document.activeElement === document.body) button.focus({ preventScroll: true });
    } finally {
        button.removeAttribute("aria-busy");
    }
});
