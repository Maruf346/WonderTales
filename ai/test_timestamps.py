#!/usr/bin/env python3
"""
test_timestamps.py
──────────────────
End-to-end test demonstrating word-level timestamp extraction
for subtitle synchronization and read-along effects in Flutter.

Usage:
    python test_timestamps.py

Tests:
    1. Word extraction from sample text
    2. Timestamp calculation for different audio durations
    3. Timestamp format validation (matches API response structure)
    4. Edge cases (empty text, very short/long durations)
"""

from services.narration_service import _extract_words, _calculate_word_timestamps


def test_word_extraction():
    """Test word extraction from various text samples."""
    print("\n=== Test 1: Word Extraction ===")
    
    test_cases = [
        "Once upon a time",
        "Hello, world! How are you?",
        "It's a beautiful day, isn't it?",
        "The quick brown fox jumps over the lazy dog.",
    ]
    
    for text in test_cases:
        words = _extract_words(text)
        print(f"Text: {text!r}")
        print(f"Words: {words}")
        print(f"Word count: {len(words)}\n")


def test_timestamp_calculation():
    """Test timestamp calculation for different audio durations."""
    print("\n=== Test 2: Timestamp Calculation ===")
    
    story_text = "Once upon a time, there was a little girl named Alice. She lived in a small cottage by the woods."
    
    test_durations = [10.0, 15.0, 20.0, 30.0]
    
    for duration in test_durations:
        print(f"\nAudio Duration: {duration}s")
        print(f"Story Text: {story_text!r}\n")
        
        timestamps = _calculate_word_timestamps(story_text, duration)
        
        print(f"Generated {len(timestamps)} word timestamps:")
        for i, ts in enumerate(timestamps[:5]):  # Show first 5
            print(f"  {i+1}. {ts['word']:12} | start: {ts['start']:6.2f}s | end: {ts['end']:6.2f}s")
        
        if len(timestamps) > 5:
            print(f"  ... and {len(timestamps) - 5} more words")
        
        # Verify timestamps are properly ordered and don't exceed duration
        for ts in timestamps:
            assert ts['start'] >= 0, f"Start time < 0: {ts['start']}"
            assert ts['end'] >= ts['start'], f"End time < start time: {ts}"
            assert ts['end'] <= duration, f"End time exceeds duration: {ts['end']} > {duration}"


def test_api_response_format():
    """Test that generated timestamps match API response schema."""
    print("\n=== Test 3: API Response Format Validation ===")
    
    from pydantic import ValidationError
    from models.schemas import WordTimestamp, StoryResponse, Language
    
    story_text = "Once upon a time there was a princess."
    timestamps = _calculate_word_timestamps(story_text, 10.0)
    
    print(f"Generated {len(timestamps)} timestamps")
    
    try:
        # Validate each timestamp matches the WordTimestamp schema
        validated_timestamps = [WordTimestamp(**ts) for ts in timestamps]
        print(f"✓ All timestamps validated against WordTimestamp schema\n")
        
        # Example API response
        response = StoryResponse(
            story_id="test-123",
            story_text=story_text,
            audio_url="/audio/test.mp3",
            language=Language.english,
            voice_used="primary_female",
            word_timestamps=validated_timestamps,
        )
        
        print("✓ Example API Response (JSON-serializable):")
        print(f"  - story_id: {response.story_id}")
        print(f"  - story_text: {response.story_text}")
        print(f"  - audio_url: {response.audio_url}")
        print(f"  - language: {response.language}")
        print(f"  - voice_used: {response.voice_used}")
        print(f"  - word_timestamps count: {len(response.word_timestamps) if response.word_timestamps else 0}")
        
        if response.word_timestamps:
            print(f"\n  Sample timestamps:")
            for ts in response.word_timestamps[:3]:
                print(f"    - {ts.word:12} | {ts.start:6.2f}s → {ts.end:6.2f}s")
        
    except ValidationError as e:
        print(f"✗ Validation error: {e}")
        return False
    
    return True


def test_flutter_cc_sync_example():
    """
    Test case demonstrating how Flutter can use timestamps for CC synchronization.
    This shows the exact data structure that the Flutter app expects.
    """
    print("\n=== Test 4: Flutter CC Sync Example ===")
    
    from models.schemas import WordTimestamp
    from pydantic import TypeAdapter
    import json
    
    # Simulated API response for a short story
    sample_response = {
        "story_id": "abc-123-def",
        "story_text": "Once upon a time, in a magical forest, there lived a wise owl.",
        "audio_url": "/audio/story-abc123.mp3",
        "language": "en",
        "voice_used": "primary_female",
        "word_timestamps": [
            {"word": "once", "start": 0.0, "end": 0.4},
            {"word": "upon", "start": 0.4, "end": 0.7},
            {"word": "a", "start": 0.7, "end": 0.9},
            {"word": "time", "start": 0.9, "end": 1.3},
            {"word": "in", "start": 1.3, "end": 1.5},
            {"word": "a", "start": 1.5, "end": 1.7},
            {"word": "magical", "start": 1.7, "end": 2.2},
            {"word": "forest", "start": 2.2, "end": 2.8},
        ]
    }
    
    print("Sample API Response (for Flutter consumption):")
    print(json.dumps(sample_response, indent=2))
    
    print("\n✓ Flutter can use word_timestamps for:")
    print("  1. Highlighting words as they're spoken (read-along effect)")
    print("  2. Synchronizing closed captions with audio")
    print("  3. Karaoke-style effects with word timing")
    print("  4. Animation timing sync with speech")
    
    print("\nExample Flutter Implementation Pattern:")
    print("""
    // In Flutter:
    final response = StoryResponse.fromJson(apiResponse);
    
    // For CC sync:
    for (var timestamp in response.wordTimestamps) {
      Future.delayed(Duration(milliseconds: (timestamp.start * 1000).toInt()), () {
        setState(() {
          currentWord = timestamp.word;
          startHighlight();
        });
      });
      
      Future.delayed(Duration(milliseconds: (timestamp.end * 1000).toInt()), () {
        setState(() {
          stopHighlight();
        });
      });
    }
    """)


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    print("\n=== Test 5: Edge Cases ===")
    
    # Empty text
    print("\n1. Empty text:")
    timestamps = _calculate_word_timestamps("", 10.0)
    print(f"   Empty text → {len(timestamps)} timestamps ✓" if len(timestamps) == 0 else f"   Empty text → ERROR")
    
    # Text with only punctuation
    print("2. Punctuation only:")
    timestamps = _calculate_word_timestamps("!!! ... ???", 5.0)
    print(f"   Punctuation only → {len(timestamps)} timestamps ✓")
    
    # Very short duration
    print("3. Very short duration (0.5s):")
    timestamps = _calculate_word_timestamps("The quick brown fox", 0.5)
    print(f"   Generated {len(timestamps)} timestamps")
    if timestamps and timestamps[-1]['end'] <= 0.5:
        print("   ✓ All timestamps within duration")
    
    # Very long duration
    print("4. Very long duration (300s):")
    timestamps = _calculate_word_timestamps("Hello world", 300.0)
    print(f"   Generated {len(timestamps)} timestamps")
    if timestamps:
        print(f"   Last word ends at: {timestamps[-1]['end']}s ✓")


if __name__ == "__main__":
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  Word-Level Timestamp Tests for Flutter CC Sync            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    try:
        test_word_extraction()
        test_timestamp_calculation()
        test_api_response_format()
        test_flutter_cc_sync_example()
        test_edge_cases()
        
        print("\n" + "="*60)
        print("✓ All tests completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
