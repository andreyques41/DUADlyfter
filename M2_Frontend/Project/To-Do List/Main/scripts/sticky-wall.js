// sticky-wall.js: Logic for Sticky Wall view
// Handles add, edit, delete, and rendering of sticky notes

const STICKY_STORAGE_KEY = "stickyNotes";

function getStickyNotes() {
	try {
		return JSON.parse(localStorage.getItem(STICKY_STORAGE_KEY)) || [];
	} catch (e) {
		return [];
	}
}

function saveStickyNotes(notes) {
	localStorage.setItem(STICKY_STORAGE_KEY, JSON.stringify(notes));
}

function renderStickyWall() {
	const wall = document.getElementById("sticky-wall");
	if (!wall) return;
	const notes = getStickyNotes();
	wall.innerHTML = "";

	// Add sticky notes
	notes.forEach((note, idx) => {
		const div = document.createElement("div");
		div.className = "sticky-note";
		const textDiv = document.createElement("div");
		textDiv.className = "sticky-note-text";
		textDiv.textContent = note.text;
		textDiv.tabIndex = 0;
		// Inline editing on click
		textDiv.addEventListener("click", (e) => {
			e.stopPropagation();
			makeStickyEditable(textDiv, idx);
		});
		textDiv.addEventListener("keydown", (e) => {
			if (e.key === "Enter") {
				e.preventDefault();
				textDiv.blur();
			}
		});
		textDiv.addEventListener("blur", () => saveStickyEdit(textDiv, idx));
		div.appendChild(textDiv);

		const btnRow = document.createElement("div");
		btnRow.className = "sticky-btn-row";

		const delBtn = document.createElement("button");
		delBtn.className = "sticky-delete-btn";
		delBtn.textContent = "Delete";
		delBtn.onclick = () => deleteStickyNote(idx);

		btnRow.appendChild(delBtn);
		div.appendChild(btnRow);

		wall.appendChild(div);
	});

	// Add the 'add new sticky' button styled as a sticky note
	const addDiv = document.createElement("div");
	addDiv.className = "sticky-note sticky-add-btn";
	addDiv.tabIndex = 0;
	addDiv.innerHTML =
		'<div class="sticky-note-text sticky-add-placeholder">+ Add new note</div>';
	addDiv.addEventListener("click", (e) => {
		e.stopPropagation();
		makeStickyEditable(addDiv, null);
	});
	addDiv.addEventListener("keydown", (e) => {
		if (e.key === "Enter") {
			e.preventDefault();
			addDiv.blur();
		}
	});
	addDiv.addEventListener("blur", () => saveStickyEdit(addDiv, null));
	wall.appendChild(addDiv);
}

function makeStickyEditable(div, idx) {
	let text = "";
	if (idx === null) {
		// Add new
		text = "";
	} else {
		text = getStickyNotes()[idx]?.text || "";
	}
	const input = document.createElement("textarea");
	input.className = "sticky-edit-area";
	input.value = text;
	input.rows = 3;
	input.style.width = "100%";
	input.style.fontFamily = "inherit";
	input.style.fontSize = "1.05rem";
	input.addEventListener("keydown", (e) => {
		if (e.key === "Enter") {
			e.preventDefault();
			input.blur();
		}
	});
	input.addEventListener("blur", () => {
		if (idx === null) {
			saveStickyEdit(input, null);
		} else {
			saveStickyEdit(input, idx);
		}
	});
	div.innerHTML = "";
	div.appendChild(input);
	input.focus();
	input.select();
}

function saveStickyEdit(inputDiv, idx) {
	const value =
		inputDiv.value !== undefined ? inputDiv.value : inputDiv.textContent;
	if (idx === null) {
		// Add new note
		if (value && value.trim()) {
			const notes = getStickyNotes();
			notes.push({ text: value.trim() });
			saveStickyNotes(notes);
		}
	} else {
		// Edit existing note
		const notes = getStickyNotes();
		if (notes[idx] && value && value.trim()) {
			notes[idx].text = value.trim();
			saveStickyNotes(notes);
		}
	}
	renderStickyWall();
}

function deleteStickyNote(idx) {
	const notes = getStickyNotes();
	notes.splice(idx, 1);
	saveStickyNotes(notes);
	renderStickyWall();
}

document.addEventListener("DOMContentLoaded", () => {
	// No need to bind add-sticky-btn, handled by renderStickyWall
	if (document.getElementById("sticky-wall")) renderStickyWall();
});

window.renderStickyWall = renderStickyWall;
