/*
For all td cells within the table.range we want to do the following
- When clicking a cell the 'marked' class should be toggled.
- When clicking and dragging it should also be toggled but only
  depending on the first cell (i.e. either mark or unmark all of them).
*/
function setupDragging() {
    function handleStart(e) {
        if ((e instanceof MouseEvent && e.button !== 0) || (e.touches && e.touches.length > 1)) {
            return;  // Not the primary button or single touch, ignore the event
        }
        e.preventDefault();
        dragging = true;
        if (!this.classList.contains('marked')) {
            this.classList.add('marked');
            isMarking = true;
        } else {
            this.classList.remove('marked');
            isMarking = false;
        }
    }

    function handleMove(e) {
        if (dragging) {
            let target;
            if (e instanceof MouseEvent) {
                target = e.target;
            } else if (e instanceof TouchEvent && e.touches.length > 0) {
                target = document.elementFromPoint(e.touches[0].clientX, e.touches[0].clientY);
            }
            if (target && target.nodeName === 'TD' && target.closest('table.range')) {
                if (isMarking) {
                    target.classList.add('marked');
                } else {
                    target.classList.remove('marked');
                }
            }
        }
    }

    function handleEnd(e) {
        if ((e instanceof MouseEvent && e.button === 0) || e instanceof TouchEvent) {
            dragging = false;
        }
    }

    let dragging = false;
    let isMarking = true;
    document.querySelectorAll('table.range.markable td').forEach(cell => {
        cell.addEventListener('mousedown', handleStart);
        cell.addEventListener('touchstart', handleStart);
        cell.addEventListener('mousemove', handleMove);
        cell.addEventListener('touchmove', handleMove);
    });
    document.addEventListener('mouseup', handleEnd);
    document.addEventListener('touchend', handleEnd);
}

if (typeof onUpdateHook !== 'undefined') {
    onUpdateHook.push(setupDragging);
} else {
    setupDragging();
}
