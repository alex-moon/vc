<div class="request-form">
    <h2>
        Create virtual content
        <span class="material-icons">expand_more</span>
    </h2>
    <form>
        <div class="texts">
            <div class="text-input">
                <h3>Add text</h3>
                <textarea placeholder="e.g. A medieval cathedral interior"></textarea>
                <button class="material-icons">
                    add_circle
                </button>
            </div>
            <vc-chipset removable></vc-chipset>
        </div>
        <div class="styles">
            <div class="text-input">
                <h3>Add style</h3>
                <input placeholder="e.g. Ansel Adams"/>
                <button class="material-icons">
                    add_circle
                </button>
            </div>
            <vc-chipset removable></vc-chipset>
        </div>
        <div class="actions">
            <button type="submit">Save</button>
        </div>
    </form>
</div>