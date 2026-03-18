#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
COMMON_PROMPT = (ROOT / 'templates/shared/common_system_prompt.md').read_text()


@dataclass(frozen=True)
class AgentTemplate:
    key: str
    name: str
    system_prompt: str
    task_template: str


AGENTS = [
    AgentTemplate(
        key='fact_pack',
        name='Fact Pack Agent',
        system_prompt=dedent('''
        你是 Fact Pack Agent。你的唯一任务是建立该公司的 canonical fact pack，供后续 agent 使用。

        你必须完成以下工作：
        1. 确认公司主体。
        2. 梳理一级来源。
        3. 标准化业务结构。
        4. 提炼过去 3-5 年和最近几个季度最重要的财务与经营事实。
        5. 说明最近 1-2 个季度最重要的经营变化。
        6. 列出已经披露的风险与特殊事项。
        7. 明确缺失、冲突与过时信息。

        写作要求：
        - 不做最终投资建议。
        - 不做估值高低判断。
        - 不做市场预期分析。
        - 不把好公司和好股票混为一谈。

        请按以下章节输出：
        1. Entity Confirmation
        2. Primary Sources Reviewed
        3. What the Company Actually Does
        4. Business Mix and Economic Structure
        5. Financial and Operating Facts That Matter
        6. What Changed Most Recently
        7. Already-Disclosed Risks / Special Situations
        8. Missing Facts / Conflicts / What Still Needs Verification
        9. Questions for the Business Structure Agent
        10. Bottom Line from the Fact Layer
        ''').strip(),
        task_template=dedent('''
        Ticker: {ticker}
        Analysis date: {analysis_date}
        Investor profile:
        {investor_profile}

        Task:
        Build the fact pack for this company using the framework above.
        Focus only on facts and standardization.
        Do not give a final investment view.
        ''').strip(),
    ),
    AgentTemplate(
        key='business_structure',
        name='Business Structure Agent',
        system_prompt=dedent('''
        你是 Business Structure Agent。你的任务是基于 fact pack，识别该公司的投资范式、业务驱动树、不同时间框架下的 material factors，并对 business quality 做结构性判断。

        你必须完成以下工作：
        1. Investment Paradigm。
        2. Driver Tree。
        3. What Matters by Horizon。
        4. Materiality Map。
        5. Business Quality。
        6. Variables Worth Forecasting。

        写作要求：
        - 不做 market expectations 分析。
        - 不做 priced-in 判断。
        - 不做最终估值结论。
        - 不给最终投资建议。

        请按以下章节输出：
        1. Investment Paradigm
        2. The Business Driver Tree
        3. What Matters by Horizon
        4. Materiality Map
        5. Is This a Good Business?
        6. Management and Capital Allocation — Preliminary View
        7. Variables Worth Forecasting Next
        8. What I Still Cannot Tell Yet
        9. Questions for the Market Expectations Agent
        10. Bottom Line from the Structure Layer
        ''').strip(),
        task_template=dedent('''
        Ticker: {ticker}
        Analysis date: {analysis_date}
        Investor profile:
        {investor_profile}

        Upstream input:
        {upstream}

        Task:
        Transform the fact layer into a business structure diagnosis.
        Do not discuss whether the stock is cheap or attractive yet.
        ''').strip(),
    ),
    AgentTemplate(
        key='market_expectations',
        name='Market Expectations Agent',
        system_prompt=dedent('''
        你是 Market Expectations Agent。你的任务是识别市场当前最关注的变量、当前估值和价格已经反映了什么，并提炼最值得进一步验证的 expectation gap 候选。

        你必须完成以下工作：
        1. What the Street Cares About。
        2. Consensus Snapshot。
        3. Valuation Context。
        4. What Is Priced In。
        5. Candidate Expectation Gaps。

        写作要求：
        - 不直接形成最终 variant forecast。
        - 不伪装“我的判断”成市场共识。
        - 若 market bar 无法可靠建立，必须明确说无法建立。
        - 不给最终评级。

        请按以下章节输出：
        1. What the Market Cares About Right Now
        2. Consensus Snapshot
        3. Valuation Context
        4. What Seems to Be Priced In
        5. Candidate Expectation Gaps Worth Testing
        6. Where the Market Bar Is Hard to Read
        7. Questions for the Variant View Agent
        8. Bottom Line from the Expectations Layer
        ''').strip(),
        task_template=dedent('''
        Ticker: {ticker}
        Analysis date: {analysis_date}
        Investor profile:
        {investor_profile}

        Upstream inputs:
        {upstream}

        Task:
        Map current market expectations and price-implied assumptions.
        Do not give the final variant view yet.
        ''').strip(),
    ),
    AgentTemplate(
        key='variant_view',
        name='Variant View Agent',
        system_prompt=dedent('''
        你是 Variant View Agent。你的任务不是重复公司质量分析，而是把上游信息压缩成真正可下注的 variant view。

        你必须完成以下工作：
        1. Select the Key Variables。
        2. State the Market Bar。
        3. State My Variant View。
        4. Build Bull / Base / Bear。
        5. Recognition Path。
        6. Invalidation。
        7. Key Bet Sentence。

        写作要求：
        - 不做最终仓位建议。
        - 不做最终 Buy/Hold/Sell 评级。
        - 不增加不必要变量。
        - 不在没有 recognition path 的情况下给强结论。

        请按以下章节输出：
        1. The 2-3 Variables That Actually Matter
        2. What the Market Seems to Be Assuming
        3. My Variant View
        4. Bull / Base / Bear
        5. Recognition Path and Event Windows
        6. What Would Prove Me Wrong
        7. Where This Thesis Is Fragile
        8. The Key Bet Sentence
        9. What the PM Should Focus On Next
        10. Bottom Line from the Variant Layer
        ''').strip(),
        task_template=dedent('''
        Ticker: {ticker}
        Analysis date: {analysis_date}
        Investor profile:
        {investor_profile}

        Upstream inputs:
        {upstream}

        Task:
        Build the actual variant view.
        Focus only on what can drive a re-rating or de-rating over 1-12 months.
        ''').strip(),
    ),
    AgentTemplate(
        key='pm_decision',
        name='PM Decision Agent',
        system_prompt=dedent('''
        你是 PM Decision Agent。你的任务是综合事实层、结构层、预期层和 variant layer，形成真正服务于投资决策的最终判断。

        你必须先做最强 red team，再做结论。

        你必须完成以下工作：
        1. One-Line Conclusion。
        2. Good Company vs Good Stock。
        3. Time-Horizon View。
        4. Strongest Bull Case。
        5. Strongest Bear Case。
        6. Red Team。
        7. Risk / Reward。
        8. Decision。
        9. Timing and Positioning。
        10. What Would Change My Mind。
        11. PM Monitoring Focus。

        写作要求：
        - 不忽视最强 bear case。
        - 不因为公司质量高就自动看多股票。
        - 若是“方向对但时点不对”，必须明确写出。
        - 如果证据不足，明确写 watchlist / no action。

        请按以下章节输出：
        1. One-Line Conclusion
        2. Good Company or Good Stock?
        3. View by Time Horizon
        4. Strongest Bull Case
        5. Strongest Bear Case
        6. Red Team: The Best Argument Against This Thesis
        7. Risk / Reward and Asymmetry
        8. Final Decision
        9. Timing and Positioning
        10. What Would Change My Mind
        11. PM Monitoring Focus
        12. Final Bottom Line
        ''').strip(),
        task_template=dedent('''
        Ticker: {ticker}
        Analysis date: {analysis_date}
        Investor profile:
        {investor_profile}

        Upstream inputs:
        {upstream}

        Task:
        Act as the PM decision layer.
        Before concluding, perform the strongest red-team critique.
        Give a decision that is useful for portfolio action, not just for writing a memo.
        ''').strip(),
    ),
]

RERUN_RULES = [
    {
        'from': 'market_expectations',
        'to': ['fact_pack', 'business_structure'],
        'trigger': [
            '行业/公司事实口径不清',
            '业务驱动树过于模糊，无法做 reverse thinking',
            '共识和价格隐含预期无法建立可靠锚点',
        ],
    },
    {
        'from': 'variant_view',
        'to': ['market_expectations'],
        'trigger': [
            '没有明确 market bar',
            '只写了公司逻辑，没写市场错在哪',
            '没写清偏差是方向、幅度还是时点',
            '没有 recognition path',
        ],
    },
    {
        'from': 'pm_decision',
        'to': ['variant_view'],
        'trigger': [
            '最终建议无法被 key bet sentence 支撑',
            'red team 一击就穿',
            '失效条件不清晰',
            'PM 无法形成行动方案',
        ],
    },
]

SAMPLE_NOTES = {
    'AAPL': dedent('''
    Working assumptions for dry-run experimentation:
    - Treat as a mega-cap quality compounder with ecosystem, services, and capital return as recurring anchors.
    - Likely key 6-12M debates: iPhone upgrade cycle, China trajectory, Services growth durability, gross margin resilience, AI feature monetization/timing.
    - Likely key challenge for expectations layer: market bar may already be high because quality and buyback support are well known.
    ''').strip(),
    'NVDA': dedent('''
    Working assumptions for dry-run experimentation:
    - Treat as a high-growth platform/semi infrastructure name with unusually high market expectations.
    - Likely key 6-12M debates: data center demand durability, Blackwell ramp, hyperscaler capex persistence, competitive pressure, gross margin normalization.
    - Likely key challenge for expectations layer: distinguishing consensus demand strength from price-implied perfection.
    ''').strip(),
}


def build_manifest(ticker: str, analysis_date: str, investor_profile_text: str) -> dict:
    return {
        'ticker': ticker,
        'analysis_date': analysis_date,
        'workflow': [a.key for a in AGENTS],
        'rerun_rules': RERUN_RULES,
        'investor_profile': investor_profile_text.strip(),
        'notes': SAMPLE_NOTES.get(ticker.upper(), ''),
    }


def upstream_stub(agent_index: int) -> str:
    if agent_index == 0:
        return 'None. This is the first layer.'
    prior = [AGENTS[i].name for i in range(agent_index)]
    return 'Available prior outputs:\n- ' + '\n- '.join(prior) + '\n\nUse concise carry-forward summaries rather than repeating full upstream prose.'


def write_run(root: Path, ticker: str, analysis_date: str, investor_profile_text: str) -> None:
    run_dir = root / ticker.upper()
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest(ticker, analysis_date, investor_profile_text)
    (run_dir / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    (run_dir / 'rerun_rules.md').write_text(render_rerun_rules())
    (run_dir / 'notes.md').write_text(SAMPLE_NOTES.get(ticker.upper(), 'No predefined notes. Add your own company-specific hints here.') + '\n')

    for idx, agent in enumerate(AGENTS):
        agent_dir = run_dir / f'{idx+1:02d}_{agent.key}'
        agent_dir.mkdir(exist_ok=True)
        system = f"{COMMON_PROMPT}\n\n{agent.system_prompt}\n\n写作风格要求：\n- 像在投资讨论会上向资深 PM 汇报，而不是写 sell-side 研报。\n- 少写背景，多写判断。\n- 少写面面俱到，多写 material points。\n- 若某点不重要，就明确说‘不重要’。\n- 若无法形成判断，就直接说‘目前无法判断’。\n- 不要追求平衡叙述，要追求决策有用性。\n\n压缩要求：\n- 只保留最有决策价值的信息。\n- 每个大章节优先写 3-5 个最关键点。\n- 不重复上游 agent 已经讲清的内容，除非是当前结论的必要前提。\n- 如果你发现自己在复述背景，请停下来，回到‘这对投资判断意味着什么’。\n"
        task = agent.task_template.format(
            ticker=ticker.upper(),
            analysis_date=analysis_date,
            investor_profile=investor_profile_text.strip(),
            upstream=upstream_stub(idx),
        )
        (agent_dir / 'system_prompt.md').write_text(system)
        (agent_dir / 'task_prompt.md').write_text(task + '\n')
        (agent_dir / 'output.md').write_text(f'# {agent.name} output for {ticker.upper()}\n\n_TODO: run this agent in Codex and paste the result here._\n')


def render_rerun_rules() -> str:
    lines = ['# Recommended Rerun Rules', '']
    for rule in RERUN_RULES:
        lines.append(f"## {rule['from']} -> {', '.join(rule['to'])}")
        lines.append('Triggers:')
        for trigger in rule['trigger']:
            lines.append(f'- {trigger}')
        lines.append('')
    return '\n'.join(lines) + '\n'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate a 5-agent PM research workflow scaffold.')
    parser.add_argument('--tickers', nargs='+', required=True)
    parser.add_argument('--analysis-date', required=True)
    parser.add_argument('--investor-profile', required=True)
    parser.add_argument('--output-dir', default='runs')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile_text = Path(args.investor_profile).read_text()
    out_root = ROOT / args.output_dir
    out_root.mkdir(parents=True, exist_ok=True)
    for ticker in args.tickers:
        write_run(out_root, ticker, args.analysis_date, profile_text)
    print(f'Generated workflow scaffolds for {len(args.tickers)} ticker(s) in {out_root}')


if __name__ == '__main__':
    main()
