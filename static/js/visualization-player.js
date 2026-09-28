(function () {
  function parseInput(rawText) {
    const text = (rawText || '').trim();
    if (!text) {
      return { nums: [2, 7, 11, 15], target: 9 };
    }

    const numsMatch = text.match(/nums\s*[:=]\s*\[([^\]]*)\]/i);
    const targetMatch = text.match(/target\s*[:=]\s*(-?\d+)/i);

    if (numsMatch) {
      const nums = numsMatch[1]
        .split(',')
        .map((value) => Number.parseInt(value.trim(), 10))
        .filter((value) => !Number.isNaN(value));
      return { nums, target: targetMatch ? Number.parseInt(targetMatch[1], 10) : 9 };
    }

    const fallback = text.match(/\[([^\]]*)\]/);
    if (fallback) {
      const nums = fallback[1]
        .split(',')
        .map((value) => Number.parseInt(value.trim(), 10))
        .filter((value) => !Number.isNaN(value));
      return { nums, target: targetMatch ? Number.parseInt(targetMatch[1], 10) : 9 };
    }

    return { nums: [2, 7, 11, 15], target: 9 };
  }

  function formatVariableValue(value) {
    if (Array.isArray(value)) {
      return `[${value.join(', ')}]`;
    }
    if (value && typeof value === 'object') {
      return JSON.stringify(value);
    }
    return String(value);
  }

  function createArrayStructure(nums, activeIndices = [], visitedIndices = [], highlightedIndices = [], answerIndices = [], options = {}) {
    return {
      type: 'array',
      title: 'Input Array',
      annotation: options.annotation || '',
      pointers: options.pointers || [],
      items: nums.map((value, index) => ({
        value,
        index,
        active: activeIndices.includes(index),
        visited: visitedIndices.includes(index),
        highlighted: highlightedIndices.includes(index),
        answer: answerIndices.includes(index),
      })),
    };
  }

  function createHashMapStructure(entries, activeKey = null, highlightedKey = null) {
    return {
      type: 'hashmap',
      title: 'HashMap',
      entries: Object.entries(entries).map(([key, value]) => ({
        key: Number(key),
        value,
        active: Number(key) === activeKey,
        highlighted: Number(key) === highlightedKey,
      })),
    };
  }

  function createEmptySecondaryStructure() {
    return {
      type: 'empty',
      title: 'Other Data Structure',
      message: 'This walkthrough only needs the input array.',
    };
  }

  function buildTrace(type, input) {
    const nums = input.nums || [2, 7, 11, 15];
    const target = Number.isFinite(input.target) ? input.target : 9;

    if (type === 'two-sum-brute-force') {
      const steps = [];
      const workflow = (currentNode) => ({ currentNode, nodes: [{ id: 'setup', label: 'Start' }, { id: 'inspect', label: 'Inspect' }, { id: 'check', label: 'Check' }, { id: 'return', label: 'Return' }], edges: ['setup->inspect', 'inspect->check', 'check->return'] });
      steps.push({ currentLine: 3, variables: { nums, target }, mainStructure: createArrayStructure(nums), secondaryStructure: createEmptySecondaryStructure(), explanation: 'Start by comparing each element with the elements to its right.', workflow: workflow('setup') });
      for (let i = 0; i < nums.length - 1; i += 1) {
        for (let j = i + 1; j < nums.length; j += 1) {
          const sum = nums[i] + nums[j];
          const variables = { nums, target, i, j, sum };
          steps.push({ currentLine: 5, variables, mainStructure: createArrayStructure(nums, [i, j]), secondaryStructure: createEmptySecondaryStructure(), explanation: 'Check the selected pair against the target.', workflow: workflow('inspect') });
          if (sum === target) {
            steps.push({ currentLine: 6, variables: { ...variables, answer: [i, j] }, mainStructure: createArrayStructure(nums, [i, j], [], [], [i, j]), secondaryStructure: createEmptySecondaryStructure(), explanation: 'This pair matches, so return its indices.', workflow: workflow('return') });
            return steps;
          }
          steps.push({ currentLine: 5, variables: { ...variables, matches: false }, mainStructure: createArrayStructure(nums, [i, j]), secondaryStructure: createEmptySecondaryStructure(), explanation: 'Not a match; continue to the next pair.', workflow: workflow('check') });
        }
      }
      return steps;
    }

    if (type === 'two-sum-two-pointers') {
      const sortedPairs = nums.map((value, index) => ({ value, index }));
      sortedPairs.sort((a, b) => a.value - b.value);
      const steps = [];
      const workflow = (currentNode) => ({ currentNode, nodes: [{ id: 'setup', label: 'Start' }, { id: 'inspect', label: 'Inspect' }, { id: 'check', label: 'Check' }, { id: 'return', label: 'Return' }], edges: ['setup->inspect', 'inspect->check', 'check->return'] });
      const display = (left, right, sum, answer = false) => createArrayStructure(sortedPairs.map((entry) => entry.value), [left, right], [], [], answer ? [left, right] : [], {
        annotation: `WINDOW · SUM = ${sum}${answer ? ' ★ MATCH' : ''}`,
        pointers: [{ index: left, label: 'L', side: 'left' }, { index: right, label: 'R', side: 'right' }],
      });
      steps.push({ currentLine: 8, variables: { nums, target, sortedPairs }, mainStructure: createArrayStructure(nums), secondaryStructure: createEmptySecondaryStructure(), explanation: 'We sort values while preserving their original positions.', workflow: workflow('setup') });
      let left = 0;
      let right = sortedPairs.length - 1;
      while (left < right) {
        const sum = sortedPairs[left].value + sortedPairs[right].value;
        const variables = { nums, target, left, right, sum };
        steps.push({ currentLine: 13, variables, mainStructure: display(left, right, sum), secondaryStructure: createEmptySecondaryStructure(), explanation: 'Add the values at the two pointers and compare their sum to the target.', workflow: workflow('inspect') });
        if (sum === target) {
          steps.push({ currentLine: 15, variables: { ...variables, answer: [sortedPairs[left].index, sortedPairs[right].index] }, mainStructure: display(left, right, sum, true), secondaryStructure: createEmptySecondaryStructure(), explanation: 'The sum matches the target, so we return the original indices.', workflow: workflow('return') });
          break;
        }
        if (sum < target) {
          steps.push({ currentLine: 17, variables, mainStructure: display(left, right, sum), secondaryStructure: createEmptySecondaryStructure(), explanation: 'The sum is too small, so move L right to increase it.', workflow: workflow('check') });
          left += 1;
        } else {
          steps.push({ currentLine: 19, variables, mainStructure: display(left, right, sum), secondaryStructure: createEmptySecondaryStructure(), explanation: 'The sum is too large, so move R left to decrease it.', workflow: workflow('check') });
          right -= 1;
        }
      }
      return steps;
    }

    if (type === 'two-sum-hashmap') {
      const map = {};
      const steps = [];
      const addStep = (currentLine, variables, mainStructure, secondaryStructure, explanation) => {
        steps.push({ currentLine, variables, mainStructure, secondaryStructure, explanation, workflow: { currentNode: 'inspect', nodes: [{ id: 'setup', label: 'Start' }, { id: 'inspect', label: 'Inspect' }, { id: 'check', label: 'Check' }, { id: 'store', label: 'Store' }, { id: 'return', label: 'Return' }], edges: ['setup->inspect', 'inspect->check', 'check->store', 'check->return'] } });
      };

      addStep(3, { nums, target, i: null, complement: null, map: {} }, createArrayStructure(nums), createHashMapStructure({}), 'We create an empty HashMap so we can remember values that have already been seen.');
      for (let i = 0; i < nums.length; i += 1) {
        const complement = target - nums[i];
        addStep(4, { nums, target, i, complement, map: { ...map } }, createArrayStructure(nums, [i]), createHashMapStructure(map), 'We inspect the current element and compute the complement needed to reach the target.');
        if (Object.prototype.hasOwnProperty.call(map, complement)) {
          addStep(5, { nums, target, i, complement, map: { ...map } }, createArrayStructure(nums, [i]), createHashMapStructure(map), 'The complement already exists in the map, which means we found a valid pair.');
          addStep(6, { nums, target, i, complement, map: { ...map }, answer: [map[complement], i] }, createArrayStructure(nums, [i, map[complement]], [], [], [i, map[complement]]), createHashMapStructure(map), 'The algorithm returns the two indices from the HashMap and the current position.');
          break;
        }
        map[nums[i]] = i;
        addStep(7, { nums, target, i, complement, map: { ...map } }, createArrayStructure(nums, [i]), createHashMapStructure(map), 'The current value is stored in the HashMap so it can be matched later.');
      }
      return steps;
    }

    return [];
  }

  function setModalState(shell, isOpen) {
    if (!shell) {
      return;
    }
    shell.classList.toggle('is-modal', isOpen);
    shell.hidden = !isOpen;
    document.body.classList.toggle('visualization-modal-open', isOpen);
    const backdrop = document.querySelector('[data-visualization-backdrop]');
    if (backdrop) {
      backdrop.hidden = !isOpen;
    }
  }

  function bindSplitBehavior(container) {
    const shell = container.querySelector('.visualization-split-shell');
    const splitter = container.querySelector('[data-splitter]');
    if (!shell || !splitter) {
      return;
    }

    let isDragging = false;

    const setSplit = (clientX) => {
      const rect = shell.getBoundingClientRect();
      const ratio = Math.min(Math.max((clientX - rect.left) / rect.width, 0.3), 0.8);
      shell.style.setProperty('--visualization-split', `${(ratio * 100).toFixed(2)}%`);
    };

    splitter.addEventListener('pointerdown', (event) => {
      isDragging = true;
      splitter.setPointerCapture(event.pointerId);
      event.preventDefault();
    });

    splitter.addEventListener('keydown', (event) => {
      if (event.key === 'ArrowLeft') {
        const current = parseFloat(shell.style.getPropertyValue('--visualization-split') || '65%');
        shell.style.setProperty('--visualization-split', `${Math.max(current - 2, 30)}%`);
        event.preventDefault();
      }
      if (event.key === 'ArrowRight') {
        const current = parseFloat(shell.style.getPropertyValue('--visualization-split') || '65%');
        shell.style.setProperty('--visualization-split', `${Math.min(current + 2, 80)}%`);
        event.preventDefault();
      }
    });

    const stopDragging = () => {
      isDragging = false;
    };

    window.addEventListener('pointermove', (event) => {
      if (!isDragging) {
        return;
      }
      setSplit(event.clientX);
    });

    window.addEventListener('pointerup', stopDragging);
    window.addEventListener('pointercancel', stopDragging);
  }

  class VisualizationPlayer {
    constructor(container) {
      this.container = container;
      this.data = JSON.parse(container.dataset.visualization || '{}');
      this.visualization = this.data.visualization || this.data;
      if (!this.visualization || typeof this.visualization !== 'object') {
        this.visualization = {};
      }
      this.codeElement = container.querySelector('[data-code-snippet]');
      this.inputField = container.querySelector('[data-visualization-input]');
      this.playButton = container.querySelector('[data-action="play"]');
      this.pauseButton = container.querySelector('[data-action="pause"]');
      this.nextButton = container.querySelector('[data-action="next"]');
      this.previousButton = container.querySelector('[data-action="previous"]');
      this.resetButton = container.querySelector('[data-action="reset"]');
      this.closeButton = container.querySelector('[data-action="close"]');
      this.speedField = container.querySelector('[data-speed]');
      this.progressField = container.querySelector('[data-progress]');
      this.currentStepLabel = container.querySelector('[data-step-label]');
      this.currentLineLabel = container.querySelector('[data-current-line]');
      this.currentLineLabelInline = container.querySelector('[data-step-label-inline]');
      this.explanationBody = container.querySelector('[data-explanation]');
      this.variableBody = container.querySelector('[data-variables]');
      this.mainStructureBody = container.querySelector('[data-main-structure]');
      this.secondaryStructureBody = container.querySelector('[data-secondary-structure]');
      this.workflowBody = container.querySelector('[data-workflow]');
      this.speedValue = container.querySelector('[data-speed-value]');
      this.inputButton = container.querySelector('[data-apply-input]');

      this.trace = [];
      this.currentStep = 0;
      this.speedMultiplier = 1;
      this.playTimer = null;
      this._bindEvents();
      this._renderCode();
      bindSplitBehavior(this.container);
      setModalState(this.container, false);
      this.reset();
    }

    _bindEvents() {
      this.playButton?.addEventListener('click', () => this.play());
      this.pauseButton?.addEventListener('click', () => this.pause());
      this.nextButton?.addEventListener('click', () => this.next());
      this.previousButton?.addEventListener('click', () => this.previous());
      this.resetButton?.addEventListener('click', () => this.reset());
      this.closeButton?.addEventListener('click', () => setModalState(this.container, false));
      this.inputButton?.addEventListener('click', () => this.applyInput());
      this.speedField?.addEventListener('input', (event) => {
        const value = Number(event.target.value);
        this.speedMultiplier = value;
        if (this.speedValue) {
          this.speedValue.textContent = `${value.toFixed(1)}x`;
        }
        if (this.playTimer) {
          this.play();
        }
      });
      this.progressField?.addEventListener('input', (event) => {
        const value = Number(event.target.value);
        if (!Number.isNaN(value)) {
          this.currentStep = Math.min(Math.max(value - 1, 0), this.trace.length - 1);
          this._renderStep();
        }
      });
    }

    _renderCode() {
      if (!this.codeElement) {
        return;
      }
      const source = this.codeElement.textContent.trim();
      const lines = source.split('\n');
      this.codeElement.innerHTML = lines
        .map((line, index) => `<div class="code-line" data-line-number="${index + 1}">${line || '&nbsp;'}</div>`)
        .join('');
    }

    _highlightLine(lineNumber) {
      const lines = this.container.querySelectorAll('.code-line');
      lines.forEach((line) => line.classList.toggle('active', Number(line.dataset.lineNumber) === lineNumber));
      const activeLine = this.container.querySelector(`.code-line[data-line-number="${lineNumber}"]`);
      if (activeLine) {
        activeLine.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }

    _renderStep() {
      const step = this.trace[this.currentStep];
      if (!step) {
        return;
      }

      if (this.currentStepLabel) {
        this.currentStepLabel.textContent = `Step ${this.currentStep + 1} / ${this.trace.length}`;
      }
      if (this.currentLineLabelInline) {
        this.currentLineLabelInline.textContent = `Step ${this.currentStep + 1} / ${this.trace.length}`;
      }
      if (this.currentLineLabel) {
        this.currentLineLabel.textContent = `Currently Executing: line ${step.currentLine}`;
      }
      if (this.explanationBody) {
        this.explanationBody.textContent = step.explanation;
      }

      const previousStep = this.trace[this.currentStep - 1];
      const changedVariables = previousStep ? Object.keys(step.variables).filter((name) => JSON.stringify(previousStep.variables[name]) !== JSON.stringify(step.variables[name])) : [];
      if (this.variableBody) {
        this.variableBody.innerHTML = Object.entries(step.variables)
          .map(([name, value]) => `<div class="variable-pill ${changedVariables.includes(name) ? 'changed' : ''}"><span>${name}</span><strong>${formatVariableValue(value)}</strong></div>`)
          .join('');
      }
      if (this.mainStructureBody) {
        this.mainStructureBody.innerHTML = this._renderStructure(step.mainStructure || step.dataStructures?.array || {});
      }
      if (this.secondaryStructureBody) {
        this.secondaryStructureBody.innerHTML = this._renderStructure(step.secondaryStructure || step.dataStructures?.hashmap || createEmptySecondaryStructure());
      }
      if (this.workflowBody) {
        this.workflowBody.innerHTML = this._renderWorkflow(step.workflow || {});
      }
      if (this.progressField) {
        this.progressField.max = this.trace.length;
        this.progressField.value = this.currentStep + 1;
      }
      this._highlightLine(step.currentLine);
    }

    _renderWorkflow(workflow) {
      const nodes = Array.isArray(workflow?.nodes) ? workflow.nodes : [];
      const activeNode = workflow?.currentNode || '';
      return nodes.map((node) => `<span class="visualization-node ${node.id === activeNode ? 'active' : ''}">${node.label}</span>`).join('');
    }

    _renderStructure(structure) {
      if (!structure || typeof structure !== 'object') {
        return '<div class="chip">No structure yet</div>';
      }

      if (structure.type === 'array') {
        const items = structure.items || [];
        const pointers = structure.pointers || [];
        const pointerAt = (index) => pointers.filter((pointer) => pointer.index === index);
        return `<div class="array-visual">
          ${structure.annotation ? `<div class="array-state">${structure.annotation}</div>` : ''}
          <div class="array-track" style="--array-length: ${Math.max(items.length, 1)}">
            <div class="array-row">${items.map((entry) => {
              const roles = pointerAt(entry.index).map((pointer) => `pointer-${pointer.side || 'current'}`).join(' ');
              return `<div class="array-slot"><div class="array-cell ${entry.active ? 'active' : ''} ${entry.visited ? 'visited' : ''} ${entry.answer ? 'answer' : ''} ${roles}">${entry.value}</div><span class="array-index">[${entry.index}]</span></div>`;
            }).join('')}</div>
            <div class="array-pointers">${items.map((entry) => `<div class="array-pointer-slot">${pointerAt(entry.index).map((pointer) => `<span class="array-pointer ${pointer.side || 'current'}">${pointer.label}<i>⌃</i></span>`).join('')}</div>`).join('')}</div>
          </div>
        </div>`;
      }

      if (structure.type === 'hashmap') {
        const entries = structure.entries || [];
        if (!entries.length) {
          return '<div class="chip">Empty map</div>';
        }
        return `<div class="hashmap-list">${entries.map((entry) => `<div class="hashmap-entry ${entry.active ? 'active' : ''} ${entry.highlighted ? 'highlighted' : ''}"><span>${entry.key}</span><span>→ ${entry.value}</span></div>`).join('')}</div>`;
      }

      if (structure.type === 'empty') {
        return `<div class="chip">${structure.message || 'No secondary structure needed.'}</div>`;
      }

      return `<div class="chip">${structure.title || 'Structure'}</div>`;
    }

    _prepareTrace() {
      const visualization = this.visualization || {};
      const input = parseInput(this.inputField?.value || visualization.defaultInputText || '');
      const steps = Array.isArray(visualization.steps) && visualization.steps.length > 0
        ? visualization.steps
        : buildTrace(visualization.type, input);
      this.trace = steps;
      this.currentStep = 0;
      if (this.trace.length) {
        this._renderStep();
      } else {
        if (this.currentStepLabel) {
          this.currentStepLabel.textContent = 'Step 0 / 0';
        }
        if (this.currentLineLabel) {
          this.currentLineLabel.textContent = 'Currently Executing: —';
        }
        if (this.currentLineLabelInline) {
          this.currentLineLabelInline.textContent = 'Step 0 / 0';
        }
        if (this.explanationBody) {
          this.explanationBody.textContent = 'No trace is available for this approach yet.';
        }
      }
    }

    applyInput() {
      this._prepareTrace();
    }

    play() {
      if (!this.trace.length) {
        return;
      }
      this.pause();
      const advance = () => {
        if (this.currentStep >= this.trace.length - 1) {
          this.pause();
          return;
        }
        this.currentStep += 1;
        this._renderStep();
      };
      advance();
      this.playTimer = window.setInterval(advance, 1100 / this.speedMultiplier);
    }

    pause() {
      if (this.playTimer) {
        window.clearInterval(this.playTimer);
        this.playTimer = null;
      }
    }

    next() {
      this.pause();
      if (this.currentStep < this.trace.length - 1) {
        this.currentStep += 1;
      }
      this._renderStep();
    }

    previous() {
      this.pause();
      if (this.currentStep > 0) {
        this.currentStep -= 1;
      }
      this._renderStep();
    }

    reset() {
      this.pause();
      this._prepareTrace();
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-open-visualization]').forEach((button) => {
      button.addEventListener('click', () => {
        const card = button.closest('.approach-card');
        const shell = card?.querySelector('.visualization-shell');
        setModalState(shell, true);
      });
    });

    document.querySelectorAll('[data-visualization]').forEach((container) => new VisualizationPlayer(container));

    const backdrop = document.querySelector('[data-visualization-backdrop]');
    backdrop?.addEventListener('click', () => {
      document.querySelectorAll('.visualization-shell.is-modal').forEach((shell) => setModalState(shell, false));
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        document.querySelectorAll('.visualization-shell.is-modal').forEach((shell) => setModalState(shell, false));
      }
    });
  });
})();
