DEFAULT_CSS = """
.row {
    display: flex;
}
.column {
    flex: 50%;
    font-size: 12px;
}
.column_left {
    text-align: left;
}
.column_right {
    text-align: right;
}
small {
    font-size: 11px;
}

.row img {
    max-width: 100%;
}
.row img + img {
    margin-left: 5px;
}
@media (max-width: 600px) {
    .row img {
        max-width: 150px;
    }
}

table.range, table.legend {
    border-collapse: collapse;
    font-size: 0.7em;
    font-family: monospace;
}
table.range td, table.legend td {
    border: 1px solid black;
    padding: 1px;
    text-align: center;
    width: 25px;
    height: 25px;
    box-sizing: border-box;
    overflow: hidden;
}
table.range:hover td {
    cursor: pointer;
}
td {
    background-color: white;
}
table.legend th {
    text-align: left;
    padding: 5px;
}
table.range td.pair {
    border: 2px solid black;
}
table.range td.center {
    font-weight: bold;
    font-size: 1.3em;
}
td.fold {
    background-color: #D6D2D2;
}
td.call {
    background-color: #4BE488;
}
td.raise {
    background-color: #FF6A6A;
}
td.marked {
    background: repeating-linear-gradient(
        45deg,
        white,
        white 3px,
        #00000070 3px,
        #00000070 6px
    );
}
td.marked.fold {
    background: repeating-linear-gradient(
        45deg,
        #D6D2D2,
        #D6D2D2 3px,
        #00000070 3px,
        #00000070 6px
    );
}
td.marked.call {
    background: repeating-linear-gradient(
        45deg,
        #4BE488,
        #4BE488 3px,
        #00000070 3px,
        #00000070 6px
    );
}
td.marked.raise {
    background: repeating-linear-gradient(
        45deg,
        #FF6A6A,
        #FF6A6A 3px,
        #00000070 3px,
        #00000070 6px
    );
}
td.blank {
    /* Blanking a cell must have priority */
    background-color: white !important;
}
td.marked.blank {
    background: repeating-linear-gradient(
        45deg,
        white,
        white 3px,
        #00000070 3px,
        #00000070 6px
    ) !important;
}
""".lstrip()


DEFAULT_JS = """
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
""".lstrip()


BLANK_TABLE = """<table class="markable range">
    <tr>
        <td class="blank pair">AA</td>
        <td class="blank suited">AKs</td>
        <td class="blank suited">AQs</td>
        <td class="blank suited">AJs</td>
        <td class="blank suited">ATs</td>
        <td class="blank suited">A9s</td>
        <td class="blank suited">A8s</td>
        <td class="blank suited">A7s</td>
        <td class="blank suited">A6s</td>
        <td class="blank suited">A5s</td>
        <td class="blank suited">A4s</td>
        <td class="blank suited">A3s</td>
        <td class="blank suited">A2s</td>
    </tr>
    <tr>
        <td class="blank offsuit">AKo</td>
        <td class="blank pair">KK</td>
        <td class="blank suited">KQs</td>
        <td class="blank suited">KJs</td>
        <td class="blank suited">KTs</td>
        <td class="blank suited">K9s</td>
        <td class="blank suited">K8s</td>
        <td class="blank suited">K7s</td>
        <td class="blank suited">K6s</td>
        <td class="blank suited">K5s</td>
        <td class="blank suited">K4s</td>
        <td class="blank suited">K3s</td>
        <td class="blank suited">K2s</td>
    </tr>
    <tr>
        <td class="blank offsuit">AQo</td>
        <td class="blank offsuit">KQo</td>
        <td class="blank pair">QQ</td>
        <td class="blank suited">QJs</td>
        <td class="blank suited">QTs</td>
        <td class="blank suited">Q9s</td>
        <td class="blank suited">Q8s</td>
        <td class="blank suited">Q7s</td>
        <td class="blank suited">Q6s</td>
        <td class="blank suited">Q5s</td>
        <td class="blank suited">Q4s</td>
        <td class="blank suited">Q3s</td>
        <td class="blank suited">Q2s</td>
    </tr>
    <tr>
        <td class="blank offsuit">AJo</td>
        <td class="blank offsuit">KJo</td>
        <td class="blank offsuit">QJo</td>
        <td class="blank pair">JJ</td>
        <td class="blank suited">JTs</td>
        <td class="blank suited">J9s</td>
        <td class="blank suited">J8s</td>
        <td class="blank suited">J7s</td>
        <td class="blank suited">J6s</td>
        <td class="blank suited">J5s</td>
        <td class="blank suited">J4s</td>
        <td class="blank suited">J3s</td>
        <td class="blank suited">J2s</td>
    </tr>
    <tr>
        <td class="blank offsuit">ATo</td>
        <td class="blank offsuit">KTo</td>
        <td class="blank offsuit">QTo</td>
        <td class="blank offsuit">JTo</td>
        <td class="blank pair">TT</td>
        <td class="blank suited">T9s</td>
        <td class="blank suited">T8s</td>
        <td class="blank suited">T7s</td>
        <td class="blank suited">T6s</td>
        <td class="blank suited">T5s</td>
        <td class="blank suited">T4s</td>
        <td class="blank suited">T3s</td>
        <td class="blank suited">T2s</td>
    </tr>
    <tr>
        <td class="blank offsuit">A9o</td>
        <td class="blank offsuit">K9o</td>
        <td class="blank offsuit">Q9o</td>
        <td class="blank offsuit">J9o</td>
        <td class="blank offsuit">T9o</td>
        <td class="blank pair">99</td>
        <td class="blank suited">98s</td>
        <td class="blank suited">97s</td>
        <td class="blank suited">96s</td>
        <td class="blank suited">95s</td>
        <td class="blank suited">94s</td>
        <td class="blank suited">93s</td>
        <td class="blank suited">92s</td>
    </tr>
    <tr>
        <td class="blank offsuit">A8o</td>
        <td class="blank offsuit">K8o</td>
        <td class="blank offsuit">Q8o</td>
        <td class="blank offsuit">J8o</td>
        <td class="blank offsuit">T8o</td>
        <td class="blank offsuit">98o</td>
        <td class="blank pair center">88</td>
        <td class="blank suited">87s</td>
        <td class="blank suited">86s</td>
        <td class="blank suited">85s</td>
        <td class="blank suited">84s</td>
        <td class="blank suited">83s</td>
        <td class="blank suited">82s</td>
    </tr>
    <tr>
        <td class="blank offsuit">A7o</td>
        <td class="blank offsuit">K7o</td>
        <td class="blank offsuit">Q7o</td>
        <td class="blank offsuit">J7o</td>
        <td class="blank offsuit">T7o</td>
        <td class="blank offsuit">97o</td>
        <td class="blank offsuit">87o</td>
        <td class="blank pair">77</td>
        <td class="blank suited">76s</td>
        <td class="blank suited">75s</td>
        <td class="blank suited">74s</td>
        <td class="blank suited">73s</td>
        <td class="blank suited">72s</td>
    </tr>
    <tr>
        <td class="blank offsuit">A6o</td>
        <td class="blank offsuit">K6o</td>
        <td class="blank offsuit">Q6o</td>
        <td class="blank offsuit">J6o</td>
        <td class="blank offsuit">T6o</td>
        <td class="blank offsuit">96o</td>
        <td class="blank offsuit">86o</td>
        <td class="blank offsuit">76o</td>
        <td class="blank pair">66</td>
        <td class="blank suited">65s</td>
        <td class="blank suited">64s</td>
        <td class="blank suited">63s</td>
        <td class="blank suited">62s</td>
    </tr>
    <tr>
        <td class="blank offsuit">A5o</td>
        <td class="blank offsuit">K5o</td>
        <td class="blank offsuit">Q5o</td>
        <td class="blank offsuit">J5o</td>
        <td class="blank offsuit">T5o</td>
        <td class="blank offsuit">95o</td>
        <td class="blank offsuit">85o</td>
        <td class="blank offsuit">75o</td>
        <td class="blank offsuit">65o</td>
        <td class="blank pair">55</td>
        <td class="blank suited">54s</td>
        <td class="blank suited">53s</td>
        <td class="blank suited">52s</td>
    </tr>
    <tr>
        <td class="blank offsuit">A4o</td>
        <td class="blank offsuit">K4o</td>
        <td class="blank offsuit">Q4o</td>
        <td class="blank offsuit">J4o</td>
        <td class="blank offsuit">T4o</td>
        <td class="blank offsuit">94o</td>
        <td class="blank offsuit">84o</td>
        <td class="blank offsuit">74o</td>
        <td class="blank offsuit">64o</td>
        <td class="blank offsuit">54o</td>
        <td class="blank pair">44</td>
        <td class="blank suited">43s</td>
        <td class="blank suited">42s</td>
    </tr>
    <tr>
        <td class="blank offsuit">A3o</td>
        <td class="blank offsuit">K3o</td>
        <td class="blank offsuit">Q3o</td>
        <td class="blank offsuit">J3o</td>
        <td class="blank offsuit">T3o</td>
        <td class="blank offsuit">93o</td>
        <td class="blank offsuit">83o</td>
        <td class="blank offsuit">73o</td>
        <td class="blank offsuit">63o</td>
        <td class="blank offsuit">53o</td>
        <td class="blank offsuit">43o</td>
        <td class="blank pair">33</td>
        <td class="blank suited">32s</td>
    </tr>
    <tr>
        <td class="blank offsuit">A2o</td>
        <td class="blank offsuit">K2o</td>
        <td class="blank offsuit">Q2o</td>
        <td class="blank offsuit">J2o</td>
        <td class="blank offsuit">T2o</td>
        <td class="blank offsuit">92o</td>
        <td class="blank offsuit">82o</td>
        <td class="blank offsuit">72o</td>
        <td class="blank offsuit">62o</td>
        <td class="blank offsuit">52o</td>
        <td class="blank offsuit">42o</td>
        <td class="blank offsuit">32o</td>
        <td class="blank pair">22</td>
    </tr>
</table>
"""
