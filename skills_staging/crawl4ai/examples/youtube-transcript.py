#!/usr/bin/env python3
"""
YouTube Transcript Extractor - Extract transcripts from YouTube videos.

This script extracts video metadata and transcripts from YouTube pages.
Note: YouTube transcripts require JavaScript rendering to access.

Usage:
    python youtube-transcript.py <youtube-url>
    python youtube-transcript.py --batch videos.txt --output ./transcripts
    python youtube-transcript.py https://youtu.be/VIDEO_ID --format srt
"""

import argparse
import asyncio
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, parse_qs

try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
except ImportError:
    print("Error: crawl4ai not installed. Run: pip install crawl4ai")
    sys.exit(1)


class YouTubeTranscriptExtractor:
    """Extract transcripts and metadata from YouTube videos."""

    def __init__(self, output_dir: str = "./youtube_transcripts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from various YouTube URL formats."""
        patterns = [
            r'(?:v=|\/)([a-zA-Z0-9_-]{11})',  # Standard & embed
            r'youtu\.be\/([a-zA-Z0-9_-]{11})',  # Short link
            r'v\/([a-zA-Z0-9_-]{11})',  # Old format
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    async def extract_video_metadata(self, url: str) -> Dict[str, Any]:
        """Extract video metadata using JavaScript."""
        js_extraction = """
        async () => {
            const data = {};

            // Extract title
            const title = document.querySelector('h1')?.textContent ||
                         document.querySelector('#title h2')?.textContent ||
                         document.querySelector('meta[property="og:title"]')?.content;
            data.title = title?.trim();

            // Extract channel name
            data.channel = document.querySelector('#channel-name a')?.textContent ||
                          document.querySelector('[itemprop="author"]')?.content ||
                          document.querySelector('meta[name="author"]')?.content;

            // Extract view count
            const viewText = document.querySelector('#count .view-count')?.textContent ||
                            document.querySelector('.view-count')?.textContent;
            data.view_count = viewText?.trim();

            // Extract publish date
            data.publish_date = document.querySelector('#date [slot="date"]')?.textContent ||
                               document.querySelector('meta[itemprop="uploadDate"]')?.content;

            // Extract description
            data.description = document.querySelector('#description')?.textContent ||
                              document.querySelector('meta[name="description"]')?.content;

            // Extract thumbnail
            data.thumbnail = document.querySelector('meta[property="og:image"]')?.content;

            // Extract duration
            data.duration = document.querySelector('.length')?.textContent;

            // Extract likes
            data.likes = document.querySelector('#top-level-buttons-computed button')?.textContent;

            return data;
        }
        """

        browser_config = BrowserConfig(
            headless=True,
            viewport_width=1280,
            viewport_height=720,
        )
        crawler_config = CrawlerRunConfig(
            js_code=js_extraction,
            page_timeout=30000,
            wait_for="networkidle",
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=crawler_config)

            if result.success:
                return result.js_result or {}

        return {"error": "Failed to extract metadata"}

    async def extract_transcript_js(self, url: str) -> Dict[str, Any]:
        """
        Attempt to extract transcript using JavaScript.
        Note: YouTube may require specific handling for transcripts.
        """
        js_transcript = """
        async () => {
            const result = {
                transcript_found: false,
                subtitles: [],
                error: null
            };

            try {
                // Check for caption button
                const captionBtn = document.querySelector('[aria-label="Show subtitles"]') ||
                                   document.querySelector('.ytp-subtitles-button');

                if (captionBtn) {
                    result.caption_button_found = true;

                    // Get caption tracks from player
                    const player = document.querySelector('#movie_player');
                    if (player && player.getOption) {
                        const tracks = player.getOption('captions', 'tracklist') || [];
                        result.tracks = tracks.map(t => ({
                            languageCode: t.languageCode,
                            languageName: t.languageName
                        }));
                    }
                }

                // Try to find transcript in page
                const transcriptSection = document.querySelector('[target-id="watch-transcript"]') ||
                                         document.querySelector('.ytd-transcript-segment-list-renderer');

                if (transcriptSection) {
                    result.transcript_found = true;

                    // Extract caption segments
                    const segments = transcriptSection.querySelectorAll('ytd-transcript-segment-renderer, .segment');
                    segments.forEach((seg, i) => {
                        const text = seg.querySelector('.segment-text, .caption-display')?.textContent;
                        const start = seg.getAttribute('start-ms') || seg.getAttribute('data-start');
                        if (text) {
                            result.subtitles.push({
                                index: i,
                                text: text.trim(),
                                start_ms: start
                            });
                        }
                    });
                }

            } catch (e) {
                result.error = e.message;
            }

            return result;
        }
        """

        browser_config = BrowserConfig(
            headless=True,
            viewport_width=1280,
            viewport_height=720,
        )
        crawler_config = CrawlerRunConfig(
            js_code=js_transcript,
            page_timeout=60000,
            wait_for="networkidle",
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=crawler_config)

            if result.success:
                return result.js_result or {}

        return {"error": "Failed to extract transcript"}

    def format_timestamp(self, seconds: float) -> str:
        """Convert seconds to SRT timestamp format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        ms = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

    def format_timestamp_vtt(self, seconds: float) -> str:
        """Convert seconds to VTT timestamp format."""
        return self.format_timestamp(seconds).replace(',', '.')

    def generate_srt(self, subtitles: List[Dict], video_title: str) -> str:
        """Generate SRT formatted transcript."""
        lines = []

        for i, sub in enumerate(subtitles, 1):
            start = self.format_timestamp(float(sub.get('start_ms', 0)) / 1000)
            end = self.format_timestamp((float(sub.get('start_ms', 0)) / 1000) + 3)

            lines.append(str(i))
            lines.append(f"{start} --> {end}")
            lines.append(sub.get('text', ''))
            lines.append("")

        return "\n".join(lines)

    def generate_vtt(self, subtitles: List[Dict], video_title: str) -> str:
        """Generate VTT formatted transcript."""
        lines = [
            "WEBVTT",
            "",
            f"Title: {video_title}",
            f"Created: {datetime.now().isoformat()}",
            "",
        ]

        for i, sub in enumerate(subtitles, 1):
            start = self.format_timestamp_vtt(float(sub.get('start_ms', 0)) / 1000)
            end = self.format_timestamp_vtt((float(sub.get('start_ms', 0)) / 1000) + 3)

            lines.append(f"{i}")
            lines.append(f"{start} --> {end}")
            lines.append(sub.get('text', ''))
            lines.append("")

        return "\n".join(lines)

    def generate_json_transcript(
        self, metadata: Dict, transcript_data: Dict, subtitles: List[Dict]
    ) -> Dict:
        """Generate JSON transcript with metadata."""
        return {
            "video": {
                "title": metadata.get("title", ""),
                "url": metadata.get("url", ""),
                "channel": metadata.get("channel", ""),
                "publish_date": metadata.get("publish_date", ""),
                "view_count": metadata.get("view_count", ""),
                "duration": metadata.get("duration", ""),
                "description": metadata.get("description", "")[:500],
            },
            "transcript": {
                "language": "en",  # Would need detection
                "subtitles": [
                    {"text": sub.get("text", ""), "timestamp_ms": sub.get("start_ms")}
                    for sub in subtitles
                ],
                "extracted_at": datetime.now().isoformat(),
                "subtitle_count": len(subtitles),
            },
        }

    async def process_video(
        self, url: str, output_format: str = "json"
    ) -> Dict[str, Any]:
        """Process a single video URL."""
        video_id = self.extract_video_id(url)

        print(f"Processing video: {url}")
        print(f"Video ID: {video_id}")

        # Extract metadata
        metadata = await self.extract_video_metadata(url)
        metadata["url"] = url
        metadata["video_id"] = video_id

        print(f"Title: {metadata.get('title', 'Unknown')}")

        # Extract transcript
        transcript_data = await self.extract_transcript_js(url)

        subtitles = transcript_data.get("subtitles", [])

        if subtitles:
            print(f"Found {len(subtitles)} subtitle segments")

            # Generate output files
            title = re.sub(r'[<>:"/\\|?*]', '_', metadata.get("title", video_id)[:50])

            if output_format in ["json", "all"]:
                json_data = self.generate_json_transcript(metadata, transcript_data, subtitles)
                json_file = self.output_dir / f"{title}.json"
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                print(f"Saved JSON: {json_file}")

            if output_format in ["srt", "all"]:
                srt_content = self.generate_srt(subtitles, metadata.get("title", ""))
                srt_file = self.output_dir / f"{title}.srt"
                with open(srt_file, "w", encoding="utf-8") as f:
                    f.write(srt_content)
                print(f"Saved SRT: {srt_file}")

            if output_format in ["vtt", "all"]:
                vtt_content = self.generate_vtt(subtitles, metadata.get("title", ""))
                vtt_file = self.output_dir / f"{title}.vtt"
                with open(vtt_file, "w", encoding="utf-8") as f:
                    f.write(vtt_content)
                print(f"Saved VTT: {vtt_file}")
        else:
            print("No transcript found on page")
            print(f"Transcript data: {transcript_data}")

        return {
            "video_id": video_id,
            "metadata": metadata,
            "transcript_found": len(subtitles) > 0,
            "subtitle_count": len(subtitles),
            "output_dir": str(self.output_dir),
        }


async def batch_process(urls: List[str], output_dir: str, output_format: str):
    """Process multiple video URLs."""
    extractor = YouTubeTranscriptExtractor(output_dir)
    results = []

    for url in urls:
        url = url.strip()
        if not url or not extractor.extract_video_id(url):
            continue

        result = await extractor.process_video(url, output_format)
        results.append(result)

        # Rate limiting
        await asyncio.sleep(2)

    # Save batch report
    report_file = Path(output_dir) / "batch_report.json"
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nBatch complete. Report saved to: {report_file}")
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Extract YouTube video transcripts and metadata"
    )
    parser.add_argument("url", nargs="?", help="YouTube video URL")
    parser.add_argument(
        "--output", "-o", default="./youtube_transcripts", help="Output directory"
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "srt", "vtt", "all"],
        default="json",
        help="Output format",
    )
    parser.add_argument(
        "--batch", "-b", help="File containing YouTube URLs (one per line)"
    )
    parser.add_argument(
        "--metadata-only", action="store_true", help="Extract metadata only, skip transcript"
    )

    args = parser.parse_args()

    if not any([args.url, args.batch]):
        parser.print_help()
        print("\nExamples:")
        print("  python youtube-transcript.py https://youtu.be/dQw4w9WgXcQ")
        print("  python youtube-transcript.py https://youtube.com/watch?v=XXX -f all")
        print("  python youtube-transcript.py --batch videos.txt --output ./transcripts")
        sys.exit(1)

    extractor = YouTubeTranscriptExtractor(args.output)

    if args.batch:
        with open(args.batch) as f:
            urls = f.readlines()
        results = asyncio.run(batch_process(urls, args.output, args.format))
    elif args.url:
        result = asyncio.run(extractor.process_video(args.url, args.format))
        print(f"\nProcessing complete!")
        print(f"Output directory: {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
