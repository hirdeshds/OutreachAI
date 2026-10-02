import json
import pandas as pd
from datetime import datetime
from rich.console import Console
from rich.table import Table

from config.settings import (
    RAW_DATA_PATH,
    FILTERED_DATA_PATH,
    ENRICHED_DATA_PATH,
    MESSAGES_DATA_PATH,
    TRACKER_CSV_PATH,
    DATA_DIR
)
from src.discovery.discover import run_discovery
from src.filtering.classifier import filter_influencers, save_filtered_influencers
from src.enrichment.enricher import enrich_influencers, save_enriched_influencers
from src.personalization.generator import personalize_all, save_personalized_messages
from src.sending.email_sender import dispatch_email_outreach
from src.sending.dm_manager import prepare_dm_queue, dispatch_simulated_dm
from src.tracking.tracker import (
    get_contacted_emails,
    log_outreach_entry,
    fetch_all_outreach_logs,
    export_outreach_tracker_csv
)

import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console(highlight=False)

def export_recommended_dataset_csv(all_evaluated_influencers: list) -> str:
    rows = []
    for item in all_evaluated_influencers:
        rows.append({
            "Name": item.get("name"),
            "Platform": item.get("platform"),
            "Followers": item.get("follower_count"),
            "Engagement": f"{item.get('engagement_rate')}%",
            "Niche": item.get("category"),
            "Email": item.get("email"),
            "Profile URL": item.get("profile_url"),
            "Content Theme": ", ".join(item.get("content_themes", [])),
            "Status": item.get("status")
        })
    csv_path = DATA_DIR / "influencer_dataset.csv"
    pd.DataFrame(rows).to_csv(csv_path, index=False, encoding="utf-8")
    return str(csv_path)

def run_pipeline() -> dict:
    console.print("\n[bold cyan]====================================================[/bold cyan]")
    console.print("[bold green] Micro-Influencer Outreach System - Pipeline Run [/bold green]")
    console.print("[bold cyan]====================================================[/bold cyan]\n")

    # Step 1: Influencer Discovery
    console.print("[bold yellow]Step 1: Running Influencer Discovery...[/bold yellow]")
    discovered = run_discovery()
    console.print(f"[white][OK] Discovered [bold]{len(discovered)}[/bold] influencer profiles.[/white]\n")

    # Step 2: Filtering & Classification
    console.print("[bold yellow]Step 2: Filtering & Classifying Candidates...[/bold yellow]")
    filtering_results = filter_influencers(discovered)
    save_filtered_influencers(filtering_results)
    
    summary = filtering_results["summary"]
    console.print(f"[white][OK] Total Evaluated: [bold]{summary['total_discovered']}[/bold][/white]")
    console.print(f"[green][OK] Passed: [bold]{summary['total_passed']}[/bold][/green]")
    console.print(f"[red][X] Failed: [bold]{summary['total_failed']}[/bold][/red]")
    console.print(f"[white][OK] Pass Rate: [bold]{summary['pass_rate_pct']}%[/bold][/white]\n")

    export_recommended_dataset_csv(filtering_results["all"])

    # Step 3: Profile Enrichment
    console.print("[bold yellow]Step 3: Enriching Shortlisted Creator Profiles...[/bold yellow]")
    passed_influencers = filtering_results["passed"]
    enriched = enrich_influencers(passed_influencers)
    save_enriched_influencers(enriched)
    
    with_email_count = sum(1 for e in enriched if e["has_valid_email"])
    console.print(f"[white][OK] Enriched [bold]{len(enriched)}[/bold] profiles with metrics, angles, and demographics.[/white]")
    console.print(f"[white][OK] Profiles with valid email: [bold]{with_email_count}[/bold] | Missing email: [bold]{len(enriched) - with_email_count}[/bold][/white]\n")

    # Step 4: Message Personalization
    console.print("[bold yellow]Step 4: Generating AI-Personalized Outreach (Email + DM)...[/bold yellow]")
    personalized_messages = personalize_all(enriched)
    save_personalized_messages(personalized_messages)
    console.print(f"[white][OK] Generated [bold]{len(personalized_messages)}[/bold] email pitches (60-90 words) & Instagram DMs (15-30 words).[/white]\n")

    # Step 5: Sending Layer & Execution
    console.print("[bold yellow]Step 5: Executing Outreach Sending Layer...[/bold yellow]")
    already_sent_emails = get_contacted_emails()
    
    email_dispatch_results = []
    dm_queue = prepare_dm_queue(personalized_messages)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for msg in personalized_messages:
        dispatch_res = dispatch_email_outreach(msg, already_sent_emails, force_simulation=True)
        email_dispatch_results.append(dispatch_res)

        log_outreach_entry({
            "influencer": msg.get("influencer_name"),
            "email": msg.get("email"),
            "platform": msg.get("platform"),
            "channel": "Email",
            "message_generated": "Yes",
            "sent": dispatch_res.get("sent"),
            "date": now_str,
            "status": dispatch_res.get("status"),
            "collaboration_angle": msg.get("collaboration_angle"),
            "detail": dispatch_res.get("detail", dispatch_res.get("status"))
        })

    for dm in dm_queue:
        dm_res = dispatch_simulated_dm(dm)
        log_outreach_entry({
            "influencer": dm.get("influencer"),
            "email": "N/A (Social DM)",
            "platform": dm.get("platform"),
            "channel": "Social DM",
            "message_generated": "Yes",
            "sent": dm_res.get("sent"),
            "date": now_str,
            "status": dm_res.get("status"),
            "collaboration_angle": "Direct Message",
            "detail": dm_res.get("detail")
        })

    # Step 6: Tracking & Reporting
    console.print("[bold yellow]Step 6: Updating Outreach Tracker...[/bold yellow]")
    all_logs = fetch_all_outreach_logs()
    tracker_path = export_outreach_tracker_csv(all_logs)
    console.print(f"[green][OK] Outreach tracker updated at: [bold]{tracker_path}[/bold][/green]\n")

    table = Table(title="Pipeline Execution Summary")
    table.add_column("Stage", style="cyan")
    table.add_column("Result / Count", style="green")
    
    table.add_row("Discovered Influencers", str(len(discovered)))
    table.add_row("Passed Filtering", str(summary["total_passed"]))
    table.add_row("Failed Filtering", str(summary["total_failed"]))
    table.add_row("Enriched Profiles", str(len(enriched)))
    table.add_row("Personalized Emails Generated", str(len(personalized_messages)))
    table.add_row("Instagram / TikTok DMs Generated", str(len(personalized_messages)))
    table.add_row("Email Dispatches (Simulated/Sent)", str(len(email_dispatch_results)))
    table.add_row("Total Outreach Log Records", str(len(all_logs)))
    console.print(table)

    return {
        "discovered": len(discovered),
        "passed": summary["total_passed"],
        "failed": summary["total_failed"],
        "enriched": len(enriched),
        "messages": len(personalized_messages),
        "tracker_records": len(all_logs)
    }

if __name__ == "__main__":
    run_pipeline()
