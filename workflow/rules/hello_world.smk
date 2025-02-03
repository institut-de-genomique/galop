rule hello_world:
    output: "hello_world.txt"
    shell: "echo 'Hello, World!' > {output}"