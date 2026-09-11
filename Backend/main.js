function renderClauses(clauses) {
  const container = document.getElementById("clauses-container");
  container.innerHTML = ""; // xoá nội dung cũ

  clauses.forEach(clause => {
    const div = document.createElement("div");
    div.className = "glass-panel rounded-2xl p-5 border space-y-3";
    div.innerHTML = `
      <div class="flex justify-between">
        <span class="font-bold">${clause.title}</span>
        <span class="text-xs text-slate-400">${clause.location}</span>
      </div>
      <div class="bg-slate-950/80 p-3 rounded-xl text-xs font-mono text-slate-300">
        "${clause.text}"
      </div>
      <p class="text-xs text-slate-400">${clause.analysis}</p>
    `;
    container.appendChild(div);
  });
}
const result = await response.json();
console.log("API result:", result); // kiểm tra dữ liệu
renderClauses(result.clauses);      // render dữ liệu mới
