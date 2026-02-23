if __name__ == "__main__":
    try:
        from Interface import menu_view
    except ModuleNotFoundError as exc:
        if exc.name == "textual":
            print("Falta instalar 'textual' en el entorno virtual.")
            print("Ejecuta: source .venv/bin/activate && python -m pip install textual")
        else:
            raise
    else:
        menu_view.main()
