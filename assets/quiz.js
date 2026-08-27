/* quiz.js — shared retrieval-practice widget for the Claude Architect course.
 *
 * Usage in any lesson:
 *   <div class="quiz">
 *     <script type="application/json">
 *       [
 *         {
 *           "q": "Question text?",
 *           "answers": ["option A", "option B", ...],
 *           "correct": 0,
 *           "why": "Explanation shown after answering."
 *         }
 *       ]
 *     </script>
 *   </div>
 *   <script src="../assets/quiz.js"></script>
 *
 * The widget renders one question at a time, gives instant feedback with
 * an explanation, tracks the score, and offers a retake. Answers must be
 * authored with equal word counts so formatting gives no clues.
 */
(function () {
  "use strict";

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text != null) node.textContent = text;
    return node;
  }

  function initQuiz(container) {
    var dataScript = container.querySelector('script[type="application/json"]');
    if (!dataScript) return;
    var questions;
    try {
      questions = JSON.parse(dataScript.textContent);
    } catch (e) {
      return;
    }
    dataScript.parentNode.removeChild(dataScript);
    if (!questions.length) return;

    var score = 0;

    var header = el("div", "quiz-header");
    header.appendChild(el("span", "quiz-title", "Retrieval practice"));
    var counter = el("span", "quiz-count", "");
    header.appendChild(counter);
    container.appendChild(header);

    var stage = el("div", "quiz-stage");
    container.appendChild(stage);

    function showQuestion(i) {
      stage.innerHTML = "";
      counter.textContent = (i + 1) + " / " + questions.length;

      var item = questions[i];
      stage.appendChild(el("div", "quiz-q", item.q));

      var options = el("div", "quiz-options");
      var why = null;
      var buttons = [];

      item.answers.forEach(function (answer, idx) {
        var btn = el("button", "quiz-option", answer);
        btn.type = "button";
        btn.addEventListener("click", function () {
          buttons.forEach(function (b) { b.disabled = true; });
          var isCorrect = idx === item.correct;
          btn.classList.add(isCorrect ? "is-correct" : "is-wrong");
          if (!isCorrect) {
            buttons[item.correct].classList.add("is-reveal", "is-correct");
            btn.classList.remove("is-reveal");
          }
          if (isCorrect) score++;
          why = el("div", "quiz-why " + (isCorrect ? "correct" : "wrong"));
          var label = el("b", null, isCorrect ? "Correct. " : "Not quite. ");
          why.appendChild(label);
          why.appendChild(document.createTextNode(item.why));
          stage.appendChild(why);
          nextBtn.disabled = false;
        });
        buttons.push(btn);
        options.appendChild(btn);
      });
      stage.appendChild(options);

      var actions = el("div", "quiz-actions");
      var nextBtn = el("button", "quiz-btn", "Next question");
      nextBtn.type = "button";
      nextBtn.disabled = true;
      nextBtn.addEventListener("click", function () {
        if (i + 1 < questions.length) showQuestion(i + 1);
        else showResults();
      });
      actions.appendChild(nextBtn);
      stage.appendChild(actions);
      if (item.answers.length && buttons[item.correct]) {
        buttons[item.correct].focus && buttons[0].focus();
      }
    }

    function showResults() {
      stage.innerHTML = "";
      counter.textContent = "done";
      var pct = Math.round((score / questions.length) * 100);
      var message =
        pct === 100 ? "Perfect recall — this is stored, not just fluent." :
        pct >= 75  ? "Solid. Revisit the ones you missed tomorrow." :
        pct >= 50  ? "Halfway there — reread the section above, then retake." :
                     "Worth rereading the lesson, then trying again.";
      var scoreLine = el("div", "quiz-score");
      var strong = el("strong", null, score + " / " + questions.length);
      scoreLine.appendChild(strong);
      scoreLine.appendChild(document.createTextNode(" — " + message));
      stage.appendChild(scoreLine);

      var actions = el("div", "quiz-actions");
      var retake = el("button", "quiz-btn", "Retake");
      retake.type = "button";
      retake.addEventListener("click", function () {
        score = 0;
        showQuestion(0);
      });
      actions.appendChild(retake);
      stage.appendChild(actions);
    }

    showQuestion(0);
  }

  document.addEventListener("DOMContentLoaded", function () {
    var quizzes = document.querySelectorAll(".quiz");
    for (var i = 0; i < quizzes.length; i++) initQuiz(quizzes[i]);
  });
})();
