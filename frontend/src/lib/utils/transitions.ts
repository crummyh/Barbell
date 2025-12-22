import { expoOut } from 'svelte/easing';

function lerp(a: number, b: number, t: number) {
	return a + (b - a) * t;
}

export function countUp(
	node: HTMLElement,
	params: { delay?: number; duration?: number; goal: number; suffix?: string }
) {
	const valid = node.childNodes.length === 1 && node.childNodes[0].nodeType === Node.TEXT_NODE;

	if (!valid) {
		throw new Error(`This transition only works on elements with a single text node child`);
	}

	if (params.suffix) {
		return {
			delay: params.delay,
			duration: params.duration,
			tick: (t: number) => {
				node.textContent =
					Math.round(lerp(0, params.goal, expoOut(t))).toLocaleString() + params.suffix;
			}
		};
	} else {
		return {
			delay: params.delay,
			duration: params.duration,
			tick: (t: number) => {
				node.textContent = Math.round(lerp(0, params.goal, expoOut(t))).toLocaleString();
			}
		};
	}
}
