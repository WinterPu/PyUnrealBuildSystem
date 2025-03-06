from pathlib import Path

def find_maps_and_generate_config(project_path: Path):
    # Check Path
    content_path = project_path / "Content"
    if not content_path.exists():
        print(f"Error: Content directory not found at {content_path}")
        return

    # Find All umaps
    maps = []

    for map_file in content_path.rglob("*.umap"):
        relative_path = map_file.relative_to(content_path)
        ue_path = relative_path.with_suffix("").as_posix()
        map_entry = f'+MapsToCook=(FilePath="/Game/{ue_path}")'
        maps.append(map_entry)

    # Output
    print("\n=== MapsToCook Configuration ===\n")
    for map_path in maps:
        print(map_path)

    # Save To File
    output_file = project_path / "MapsToCook.txt"
    output_file.write_text("\n".join(maps) + "\n", encoding='utf-8')
    
    print(f"\nConfiguration has been saved to: {output_file}")
    print(f"Total maps found: {len(maps)}")

if __name__ == "__main__":
    project_path = Path("")

    find_maps_and_generate_config(project_path)